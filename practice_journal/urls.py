"""
URL configuration for practice_journal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from practice_journal.journal_core import views
from .journal_core.views import ProtectedView, CurrentUserView, UserRegistrationView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'practice-items', views.PracticeItemViewSet)
router.register(r'goals', views.GoalViewSet)

urlpatterns = [
    path("api/protected/", ProtectedView.as_view(), name="protected"),
    path('api/user/me/', CurrentUserView.as_view(), name="current-user"),
    path('api/register/', UserRegistrationView.as_view(), name="user-registration"),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('payments/', include('practice_journal.payments.urls')),
    path('api/recordings/upload-url/', views.create_presigned_upload, name='generate_persigned_upload'),
    path('api/recordings/save-recording/', views.save_recording_metadata, name='save_recording_metadata'),
]

urlpatterns += router.urls