from django.urls import path
from .views import CreateCheckoutSessionView, ConfirmSubscriptionView, StripeWebhookView, CreatePortalSessionView

urlpatterns = [
    path('stripe/webhook/', StripeWebhookView.as_view(), name="stripe-webhook"),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('confirm-subscription/', ConfirmSubscriptionView.as_view(), name='confirm-subscription'),
    path('create-portal-session/', CreatePortalSessionView.as_view(), name='create-portal-session'),
]