from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserTestCase(TestCase):
  def test_create_student_user(self):
    user = User.objects.create_user(
      username="userOne",
      email="user@test.com",
      password="testpass123",
    )

    self.assertEqual(user.username, "userOne")
    self.assertEqual(user.email, "user@test.com")
    self.assertFalse(user.is_teacher)
    self.assertEqual(user.points, 0)
    self.assertEqual(user.timezone, "Europe/London")
    self.assertIsNone(user.subscription_id)
    self.assertEqual(user.username, "userOne")
    self.assertEqual(str(user), "userOne")

  def test_create_teacher_user(self):
    user = User.objects.create_user(
        username="teacherOne",
        email="teacher@test.com",
        password="teachpass123",
        is_teacher=True
    )
    self.assertTrue(user.is_teacher)
  
  def test_custom_fields(self):
    user = User.objects.create_user(
        username="custom",
        password="pass",
        points=50,
        timezone="America/New_York",
        subscription_id="sub_123"
    )
    self.assertEqual(user.points, 50)
    self.assertEqual(user.timezone, "America/New_York")
    self.assertEqual(user.subscription_id, "sub_123")

  def test_str_representation(self):
    user = User.objects.create_user(username="testuser", password="pass")
    self.assertEqual(str(user), "testuser")


  

