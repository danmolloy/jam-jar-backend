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

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Add this to your .env

frontend_url = settings.FRONTEND_URL

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # You should have a Stripe price ID for your premium plan
            checkout_session = stripe.checkout.Session.create(
                #payment_method_types=['card'],
                line_items=[{
                    'price': 'price_1RknNQR9MFfQLnItHySRNrXX',  
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=request.user.email,
                success_url = f'{frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url = f'{frontend_url}/account'
            )
            return Response({'sessionId': checkout_session.id})
        except Exception as e:
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
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            subscription_id = session.get('subscription')
            customer_email = session.get('customer_email')
            if subscription_id and customer_email:
                try:
                    user = CustomUser.objects.get(email=customer_email)
                    user.subscription_id = subscription_id
                    user.save()
                except CustomUser.DoesNotExist:
                    pass  

        # Add more event types as needed

        return HttpResponse(status=200)