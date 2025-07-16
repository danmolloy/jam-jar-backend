from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from .models import PracticeItem, Goal
from .serializers import PracticeItemSerializer, GoalSerializer, UserRegistrationSerializer, UserUpdateSerializer, AudioRecordingSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework import status
from .utils.s3 import generate_presigned_upload_url
from django.views.decorators.csrf import csrf_exempt
User = get_user_model()

from practice_journal.journal_core.serializers import UserSerializer


class UserRegistrationView(CreateAPIView):
    """View for user registration"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'User created successfully',
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
      
      serializer = self.get_serializer(instance, data=request.data, partial=partial)
      serializer.is_valid(raise_exception=True)
      user = serializer.save()
      
      return Response({
          'message': 'User updated successfully',
          'user': {
              'id': user.id,
              'username': user.username,
              'email': user.email,
              'first_name': user.first_name,
              'last_name': user.last_name,
              'is_teacher': user.is_teacher
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
   

""" class PracticeSessionViewSet(viewsets.ModelViewSet):
    serializer_class = PracticeSessionSerializer
    permission_classes = [IsAuthenticated]
    queryset = PracticeSession.objects.all()

    def get_queryset(self):
      return PracticeSession.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
      serializer.context["student"] = self.request.user
      serializer.save() """

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