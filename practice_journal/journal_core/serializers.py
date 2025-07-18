from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import PracticeItem, Goal
from .models.diary import DiaryEntry
from .models.recording import AudioRecording
from .models.practice import achievements
from .utils.s3 import generate_presigned_download_url
from drf_spectacular.utils import extend_schema_field


User = get_user_model()
      
class PracticeItemSerializer(serializers.ModelSerializer):
   class Meta:
      model = PracticeItem
      fields = [
         'id',
         'date',
         'activity',
         'notes',
         'rating',
         'duration',
         'tags',
      ]
      read_only_fields = ['id']

   def create(self, validated_data):
      student = self.context.get("student")
      if not student:
         raise serializers.ValidationError("Student is required.")
      
      item = PracticeItem.objects.create(student=student, **validated_data)
      return item


class GoalSerializer(serializers.ModelSerializer):
   class Meta:
      model = Goal
      fields = [
         'id',
         'category',
         'title',
         'description',
         'target_count',
         'start_date',
         'end_date',
         'assigned_to',
         'assigned_by',
         'creation_date',
      ]

   def create(self, validated_data):
      assigned_by = self.context.get("assigned_by")
      if not assigned_by:
         raise serializers.ValidationError("Assigned by user is required.")
      validated_data["assigned_by"] = assigned_by
      return super().create(validated_data)
   
class DiaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryEntry
        fields = [
            'date',
            'title',
            'body', 
            'id', 
            'created_at', 
            'author'
        ]
        read_only_fields = ['id', 'created_at', 'author']


class AudioRecordingSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = AudioRecording
        fields = ['id', 'user', 's3_key', 'url', 'title', 'notes', 'tags', 'location', 'date', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    @extend_schema_field(serializers.URLField())
    def get_url(self, obj):
        if obj.s3_key:
            return generate_presigned_download_url(obj.s3_key)
        return None


class UserSerializer(serializers.HyperlinkedModelSerializer):
   full_achievements = serializers.SerializerMethodField()

   practice_items = PracticeItemSerializer(
      many=True,
      read_only=True,
   )
   recordings = AudioRecordingSerializer(
       many=True,
       read_only=True
   )
   """ achievements = AchievementSerializer(
         many=True,
         read_only=True,
      ) """
   goals = GoalSerializer(
         many=True,
         read_only=True,
      )

   class Meta:
      model = User
      fields = [
      'url', 
      'id', 
      'username', 
      'recordings',
      'email', 
      'is_teacher', 
      'points', 
      'timezone', 
      'daily_target',
      'subscription_id', 
      'subscription_status',
      'diary_entries',
      'practice_items', 
      'full_achievements', 
      'goals',
      ]

   def get_full_achievements(self, obj):
      return [
         a for a in achievements
         if a['id'] in obj.achievements
      ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password', 
            'password_confirm',
            'first_name',
            'last_name',
            'is_teacher'
        ]
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'is_teacher': {'required': False}
        }
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        """Validate that email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value
    
    def validate_username(self, value):
        """Validate that username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists")
        return value
    
    def create(self, validated_data):
        """Create and return a new user"""
        validated_data.pop('password_confirm')  # Remove password_confirm
        user = User.objects.create_user(**validated_data)
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'is_teacher',
            'current_password',
            'new_password',
            'new_password_confirm',
            'daily_target',
        ]
        extra_kwargs = {
            'username': {'required': False},
            'daily_target': {'required': False},
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'is_teacher': {'required': False}
        }

    def validate(self, attrs):
        user = self.instance
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        # If changing password, require current password and confirmation
        if new_password or new_password_confirm:
            if not current_password:
                raise serializers.ValidationError({"current_password": "Current password is required to change password."})
            if not user.check_password(current_password):
                raise serializers.ValidationError({"current_password": "Current password is incorrect."})
            if not new_password:
                raise serializers.ValidationError({"new_password": "New password is required."})
            if new_password != new_password_confirm:
                raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('new_password_confirm', None)

        if new_password:
            instance.set_password(new_password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
        
