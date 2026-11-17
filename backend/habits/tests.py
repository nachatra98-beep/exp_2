from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import Habit, HabitLog

class HabitApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='Password123!')
        self.client.force_authenticate(user=self.user1)
        self.today = date.today()

    def test_create_habit_success(self):
        data = {
            'name': 'Study for 1 hour',
            'description': 'Daily study routine',
            'category': 'Study',
            'color': '#F59E0B',
            'icon': 'book',
            'frequency': 'Daily',
            'goal': '1 time per day'
        }
        res = self.client.post('/api/habits/', data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], 'Study for 1 hour')
        self.assertEqual(res.data['completed_today'], False)
        self.assertEqual(res.data['current_streak'], 0)

    def test_duplicate_habit_name_rejected(self):
        Habit.objects.create(user=self.user1, name='Exercise')
        res = self.client.post('/api/habits/', {'name': 'Exercise'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data['errors'])

    def test_user_cannot_see_other_user_habits(self):
        Habit.objects.create(user=self.user1, name='User1 Habit')
        Habit.objects.create(user=self.user2, name='User2 Habit')

        res = self.client.get('/api/habits/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'User1 Habit')

    def test_check_and_uncheck_habit(self):
        habit = Habit.objects.create(user=self.user1, name='Drink 2L Water')
        # Check in for today
        res = self.client.post(f'/api/habits/{habit.id}/check/', {'date': str(self.today)})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['habit']['completed_today'])
        self.assertEqual(res.data['habit']['current_streak'], 1)

        # Uncheck for today
        res_del = self.client.delete(f'/api/habits/{habit.id}/check/?date={self.today}')
        self.assertEqual(res_del.status_code, status.HTTP_200_OK)
        self.assertFalse(res_del.data['habit']['completed_today'])
        self.assertEqual(res_del.data['habit']['current_streak'], 0)

    def test_streak_logic_consecutive_days(self):
        habit = Habit.objects.create(user=self.user1, name='Sleep Early')
        # Log 3 consecutive days: today, yesterday, 2 days ago
        HabitLog.objects.create(habit=habit, date=self.today - timedelta(days=2))
        HabitLog.objects.create(habit=habit, date=self.today - timedelta(days=1))
        HabitLog.objects.create(habit=habit, date=self.today)

        res = self.client.get('/api/habits/')
        self.assertEqual(res.data[0]['current_streak'], 3)
        self.assertEqual(res.data[0]['longest_streak'], 3)
        self.assertTrue(res.data[0]['completed_today'])

    def test_streak_maintained_if_done_yesterday_not_yet_today(self):
        habit = Habit.objects.create(user=self.user1, name='Reading')
        HabitLog.objects.create(habit=habit, date=self.today - timedelta(days=1))

        res = self.client.get('/api/habits/')
        self.assertEqual(res.data[0]['current_streak'], 1)
        self.assertFalse(res.data[0]['completed_today'])

    def test_streak_resets_if_neither_today_nor_yesterday_done(self):
        habit = Habit.objects.create(user=self.user1, name='Meditation')
        HabitLog.objects.create(habit=habit, date=self.today - timedelta(days=3))
        HabitLog.objects.create(habit=habit, date=self.today - timedelta(days=2))

        res = self.client.get('/api/habits/')
        self.assertEqual(res.data[0]['current_streak'], 0)
        self.assertEqual(res.data[0]['longest_streak'], 2)
