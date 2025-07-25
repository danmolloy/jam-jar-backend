from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from .models import PracticeItem, Goal
from .models.diary import DiaryEntry
from .models.recording import AudioRecording
from .serializers import PracticeItemSerializer, GoalSerializer, UserRegistrationSerializer, UserUpdateSerializer, AudioRecordingSerializer, DiaryEntrySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework import status
from .utils.s3 import generate_presigned_upload_url, delete_s3_file
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from practice_journal.journal_core.serializers import UserSerializer
from django.conf import settings
from .utils.email_utils import send_email_confirmation
import json

FRONTEND_URL = settings.FRONTEND_URL

User = get_user_model()

class UserRegistrationView(CreateAPIView):
    """View for user registration"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send email confirmation
        send_email_confirmation(user, is_new_user=True)
        
        return Response({
            'message': 'User created successfully. Please check your email to confirm your account.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": f"Hello, {request.user.username}!"})

class UserViewSet(viewsets.ModelViewSet):
  """
  API endpoint that allows users to be viewed or edited.
  """
  queryset = User.objects.all().order_by('-date_joined')
  serializer_class = UserSerializer
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
      """Only allow users to see their own data"""
      return User.objects.filter(id=self.request.user.id)

  def get_serializer_class(self):
      """Use different serializers for different actions"""
      if self.action in ['update', 'partial_update']:
          return UserUpdateSerializer
      return UserSerializer

  def update(self, request, *args, **kwargs):
      """Update user information"""
      partial = kwargs.pop('partial', False)
      instance = self.get_object()
      
      # Ensure user can only update their own data
      if instance.id != request.user.id:
          return Response({"error": "You can only update your own profile"}, status=status.HTTP_403_FORBIDDEN)
      
      # Check if email is being changed
      old_email = instance.email
      
      serializer = self.get_serializer(instance, data=request.data, partial=partial)
      serializer.is_valid(raise_exception=True)
      user = serializer.save()
      
      # If email changed, send confirmation email
      if user.email != old_email:
          user.email_confirmed = False  # Reset email confirmation
          user.save(update_fields=['email_confirmed'])
          send_email_confirmation(user, is_new_user=False)
          
          return Response({
              'message': 'User updated successfully. Please check your new email to confirm the change.',
              'user': {
                  'id': user.id,
                  'username': user.username,
                  'email': user.email,
                  'first_name': user.first_name,
                  'last_name': user.last_name,
                  'is_teacher': user.is_teacher,
                  'email_confirmed': user.email_confirmed
              }
          }, status=status.HTTP_200_OK)
      
      return Response({
          'message': 'User updated successfully',
          'user': {
              'id': user.id,
              'username': user.username,
              'email': user.email,
              'first_name': user.first_name,
              'last_name': user.last_name,
              'is_teacher': user.is_teacher,
              'email_confirmed': user.email_confirmed
          }
      }, status=status.HTTP_200_OK)

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS and obj.user == request.user



class CurrentUserView(APIView):
   permission_classes = [IsAuthenticated]

   def get(self, request):
      serializer = UserSerializer(request.user, context={'request': request})
      return Response(serializer.data)
   

@api_view(["GET"])
@permission_classes([AllowAny])
def check_username_availability(request):
    """Check if a username is available"""
    username = request.GET.get('username', '').strip()
    
    if not username:
        return Response({
            'available': False,
            'message': 'Username is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if username exists
    exists = User.objects.filter(username=username).exists()
    
    return Response({
        'available': not exists,
        'message': 'Username is available' if not exists else 'Username is already taken'
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def confirm_email(request):
    """Confirm email address with token"""
    token = request.data.get('token')
    
    if not token:
        return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email_confirmation_token=token)
        
        if not user.is_email_confirmation_token_valid():
            return Response({"error": "Token has expired. Please request a new confirmation email."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Confirm the email
        user.email_confirmed = True
        user.email_confirmation_token = None
        user.email_confirmation_sent_at = None
        user.save(update_fields=['email_confirmed', 'email_confirmation_token', 'email_confirmation_sent_at'])
        
        return Response({"message": "Email confirmed successfully!"}, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def resend_email_confirmation(request):
    """Resend email confirmation"""
    user = request.user
    
    if user.email_confirmed:
        return Response({"error": "Email is already confirmed"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Send confirmation email
    if send_email_confirmation(user, is_new_user=False):
        return Response({"message": "Confirmation email sent successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to send confirmation email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete user account and all associated data"""
    user = request.user
    
    try:
        # Delete all audio recordings from S3
        recordings = AudioRecording.objects.filter(user=user)
        for recording in recordings:
            if recording.s3_key:
                try:
                    delete_s3_file(recording.s3_key)
                except Exception as e:
                    print(f"Error deleting S3 file {recording.s3_key}: {e}")
        
        # Delete all user data (this will cascade to related objects)
        user.delete()
        
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": f"Failed to delete account: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiaryEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DiaryEntrySerializer
    permission_classes = [IsAuthenticated]
    queryset = DiaryEntry.objects.all()

    def get_queryset(self):
        return DiaryEntry.objects.filter(author=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PracticeItemViewSet(viewsets.ModelViewSet):
    serializer_class = PracticeItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = PracticeItem.objects.all()

    def get_queryset(self):
        return PracticeItem.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
      serializer.context["student"] = self.request.user
      item = serializer.save() 
      item.award_achievements()

class GoalViewSet(viewsets.ModelViewSet):
   serializer_class = GoalSerializer
   permission_classes = [IsAuthenticated]
   queryset = Goal.objects.all()

   def get_queryset(self):
      return Goal.objects.filter(assigned_to=self.request.user)
   
   def get_serializer_context(self):
      context = super().get_serializer_context()
      context["assigned_by"] = self.request.user
      return context
   
   def perform_create(self, serializer):
      serializer.save(assigned_by=self.request.user)

class AudioRecordingViewSet(viewsets.ModelViewSet):
    serializer_class = AudioRecordingSerializer
    permission_classes = [IsAuthenticated]
    queryset = AudioRecording.objects.all()

    def get_queryset(self):
      return AudioRecording.objects.filter(user=self.request.user)
   
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def delete(self, pk):
        recording = get_object_or_404(AudioRecording, pk=pk, user=self.request.user)

        if recording.s3_key:
            delete_s3_file(recording.s3_key)

        recording.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_presigned_upload(request):
    file_name = request.data.get("file_name")
    content_type = request.data.get("content_type")

    if not file_name or not content_type:
        return Response({"error": "Missing file_name or content_type"}, status=400)
    
    url, key = generate_presigned_upload_url(file_name, content_type, request.user.id)
    
    return Response({"upload_url": url, "key": key})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_recording_metadata(request):
    data = request.data.copy()
    data['user'] = request.user.id
    serializer = AudioRecordingSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user) 
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)