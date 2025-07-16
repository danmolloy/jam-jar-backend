from django.test import TestCase
from ..models import Goal
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.core.exceptions import ValidationError

User = get_user_model()

class GoalModelTestCase(TestCase):
  def test_create_goal(self):
    user = User.objects.create_user(username="testuser", password="testpass")
    goal = Goal.objects.create(
      assigned_to = user,
      category="STREAK",
      title="Test goal",
      description="Test description",
      target_count=12,
      end_date=date.today() + timedelta(days=30),
    )
    self.assertEqual(goal.assigned_to.username, "testuser")
    self.assertEqual(goal.category, "STREAK")
    self.assertEqual(goal.title, "Test goal")
    self.assertEqual(goal.description, "Test description")
    self.assertEqual(goal.target_count, 12)
    self.assertEqual(goal.end_date, date.today() + timedelta(days=30))

  def test_str_representation(self):
    user = User.objects.create_user(username="testuser", password="testpass")
    goal = Goal.objects.create(
      assigned_to = user,
      category="STREAK",
      title="Test goal",
      description="Test description",
      target_count=12,
      end_date=date.today() + timedelta(days=30),
    )
    self.assertEqual(str(goal), "Test goal (testuser)")

  def test_invalid_category(self):
    user = User.objects.create_user(username="testuser", password="testpass")
    goal = Goal.objects.create(
      assigned_to = user,
      category="NOT_STREAK",
      title="Test goal",
      description="Test description",
      target_count=12,
      end_date=date.today() + timedelta(days=30),
    )
    with self.assertRaises(ValidationError):
      goal.full_clean()

  def test_auto_fields(self):
    user = User.objects.create_user(username="testuser", password="testpass")
    goal = Goal.objects.create(
      assigned_to = user,
      category="NOT_STREAK",
      title="Test goal",
      description="Test description",
      target_count=12,
      end_date=date.today() + timedelta(days=30),
    )
    self.assertIsNotNone(goal.start_date)
    self.assertIsNotNone(goal.creation_date)
    self.assertEqual(goal.start_date, goal.creation_date)


  def test_self_assignment(self):
    user = User.objects.create_user(username="testuser", password="testpass")
    goal = Goal.objects.create(
      assigned_to = user,
      category="NOT_STREAK",
      title="Test goal",
      description="Test description",
      target_count=12,
      end_date=date.today() + timedelta(days=30),
    )
    self.assertIsNone(goal.assigned_by)
