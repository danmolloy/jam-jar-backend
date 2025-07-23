import stripe
from django.conf import settings
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from practice_journal.journal_core.models.user import CustomUser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Add this to your .env
STRIPE_PRICE_ID = settings.STRIPE_PRICE_ID
frontend_url = settings.FRONTEND_URL

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get price ID from settings or use default
            
            checkout_session = stripe.checkout.Session.create(
                line_items=[{
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=request.user.email,
                success_url=f'{frontend_url}/',
                cancel_url=f'{frontend_url}/account'
            )
            logger.info(f"Created checkout session {checkout_session.id} for user {request.user.email}")
            return Response({'sessionId': checkout_session.id})
        except Exception as e:
            logger.error(f"Error creating checkout session for user {request.user.email}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ConfirmSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            subscription_id = checkout_session.get('subscription')
            if not subscription_id:
                return Response({'error': 'No subscription found for this session'}, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            user.subscription_id = subscription_id
            user.save()
            return Response({'success': True, 'subscription_id': subscription_id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    authentication_classes = []  # No auth for webhooks
    permission_classes = []

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not sig_header:
            logger.error("No Stripe signature header found")
            return HttpResponse(status=400)
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return HttpResponse(status=400)

        logger.info(f"Received webhook event: {event['type']}")

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            subscription_id = session.get('subscription')
            customer_email = session.get('customer_email')
            
            logger.info(f"Checkout completed - Subscription: {subscription_id}, Email: {customer_email}")
            
            if subscription_id and customer_email:
                try:
                    user = CustomUser.objects.get(email=customer_email)
                    user.subscription_id = subscription_id
                    user.subscription_status = 'active'
                    user.save()
                    logger.info(f"Updated user {user.email} with subscription {subscription_id}")
                except CustomUser.DoesNotExist:
                    logger.error(f"User with email {customer_email} not found")
                    return HttpResponse(status=404)
        
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            subscription_id = subscription.get('id')
            status = subscription.get('status')
            
            logger.info(f"Subscription updated - ID: {subscription_id}, Status: {status}")
            
            if subscription_id:
                try:
                    user = CustomUser.objects.get(subscription_id=subscription_id)
                    user.subscription_status = status
                    user.save()
                    logger.info(f"Updated subscription status for user {user.email}: {status}")
                except CustomUser.DoesNotExist:
                    logger.error(f"User with subscription {subscription_id} not found")
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            subscription_id = subscription.get('id')
            
            logger.info(f"Subscription deleted - ID: {subscription_id}")
            
            if subscription_id:
                try:
                    user = CustomUser.objects.get(subscription_id=subscription_id)
                    user.subscription_status = 'canceled'
                    user.save()
                    logger.info(f"Marked subscription as canceled for user {user.email}")
                except CustomUser.DoesNotExist:
                    logger.error(f"User with subscription {subscription_id} not found")
        
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            subscription_id = invoice.get('subscription')
            
            logger.warning(f"Invoice payment failed - Subscription: {subscription_id}")
            
            if subscription_id:
                try:
                    user = CustomUser.objects.get(subscription_id=subscription_id)
                    user.subscription_status = 'past_due'
                    user.save()
                    logger.info(f"Marked subscription as past_due for user {user.email}")
                except CustomUser.DoesNotExist:
                    logger.error(f"User with subscription {subscription_id} not found")

        return HttpResponse(status=200)


class CreatePortalSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # First, try to find existing customer by email
            customers = stripe.Customer.list(email=request.user.email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
            else:
                # Create a new customer if none exists
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                )
            
            # Create a customer portal session using customer ID
            portal_session = stripe.billing_portal.Session.create(
                customer=customer.id,
                return_url=f'{frontend_url}/account',
            )
            return Response({'url': portal_session.url})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)