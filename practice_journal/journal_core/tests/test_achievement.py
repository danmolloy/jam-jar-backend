from django.test import TestCase
from ..models import Achievement
from django.core.exceptions import ValidationError

class AchievementModelTestCase(TestCase):
  def test_create_achievement(self):
    achievement = Achievement.objects.create(
      name="Test Achievement",
      category="ONBOARDING",
      description="Test Description",
      icon="Icon Test"
    )
    self.assertEqual(achievement.name, "Test Achievement")
    self.assertEqual(achievement.category, "ONBOARDING")
    self.assertEqual(achievement.description, "Test Description")
    self.assertEqual(achievement.icon, "Icon Test")

  def test_str_representation(self):
    achievement = Achievement.objects.create(
      name="Test Achievement",
      category="ONBOARDING",
      description="Test Description",
      icon="Icon Test"
    )
    self.assertEqual(str(achievement), "Test Achievement")

  def test_invalid_category(self):
    achievement = Achievement.objects.create(
      name="Test Achievement",
      category="Not a category",
      description="Test Description",
      icon="Icon Test"
    )
    with self.assertRaises(ValidationError):
      achievement.full_clean()