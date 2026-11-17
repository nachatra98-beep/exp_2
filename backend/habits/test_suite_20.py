from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import Habit, HabitLog

class Application20Tests(TestCase):
    """
    Comprehensive 20-Test Suite for Habit Tracker Web Application.
    Validates Accountless Direct Access, Habit CRUD, Validations, Check-in / Undo,
    Streak Calculation Algorithms, Data Integrity, and Statistics.
    """

    def setUp(self):
        self.client = APIClient()
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.two_days_ago = self.today - timedelta(days=2)
        self.three_days_ago = self.today - timedelta(days=3)

    # ---------------------------------------------------------
    # 1. ACCOUNTLESS DIRECT ACCESS & PERSONA INITIALIZATION
    # ---------------------------------------------------------
    def test_tc01_direct_accountless_access_to_habits(self):
        """TC-01: Verify habits endpoint is accessible directly without login or tokens."""
        res = self.client.get('/api/habits/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)

    def test_tc02_default_persona_initialization(self):
        """TC-02: Verify default persona 'Nachatra' is automatically initialized on access."""
        res = self.client.get('/api/habits/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username='Nachatra').exists())

    # ---------------------------------------------------------
    # 2. HABIT MANAGEMENT & VALIDATION (CRUD)
    # ---------------------------------------------------------
    def test_tc03_habit_creation_standard(self):
        """TC-03: Verify creating a habit stores all fields and initializes streaks to 0."""
        payload = {
            'name': 'Study for 1 hour',
            'description': 'Daily coding and practice',
            'category': 'Study',
            'color': '#F59E0B',
            'icon': 'book',
            'frequency': 'Daily',
            'goal': '1 time per day'
        }
        res = self.client.post('/api/habits/', payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], 'Study for 1 hour')
        self.assertEqual(res.data['category'], 'Study')
        self.assertFalse(res.data['completed_today'])
        self.assertEqual(res.data['current_streak'], 0)
        self.assertEqual(res.data['longest_streak'], 0)

    def test_tc04_habit_creation_name_required(self):
        """TC-04: Verify habit creation fails when name is empty or missing."""
        payload = {'name': '   ', 'category': 'Health'}
        res = self.client.post('/api/habits/', payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data['errors'])

    def test_tc05_habit_creation_duplicate_name_rejected(self):
        """TC-05: Verify creating a duplicate habit name is rejected (FR-22)."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        Habit.objects.create(user=user, name='Drink 2L Water')
        res = self.client.post('/api/habits/', {'name': 'Drink 2L Water'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data['errors'])

    def test_tc06_habit_creation_max_length_name(self):
        """TC-06: Verify habit name exceeding 100 characters is rejected."""
        long_name = 'A' * 105
        res = self.client.post('/api/habits/', {'name': long_name})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data['errors'])

    def test_tc07_habit_description_optional(self):
        """TC-07: Verify habit description is optional and defaults gracefully."""
        res = self.client.post('/api/habits/', {'name': 'Quick Walk'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['description'], '')

    def test_tc08_habit_list_retrieval(self):
        """TC-08: Verify habit listing retrieves active habits with accurate computed fields."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        Habit.objects.create(user=user, name='Exercise')
        Habit.objects.create(user=user, name='Sleep Early')

        res = self.client.get('/api/habits/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        habit_names = [h['name'] for h in res.data]
        self.assertIn('Exercise', habit_names)
        self.assertIn('Sleep Early', habit_names)

    def test_tc09_habit_single_detail_retrieval(self):
        """TC-09: Verify retrieving a single habit by ID."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Meditation', category='Mindfulness')
        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], habit.id)
        self.assertEqual(res.data['name'], 'Meditation')

    def test_tc10_habit_update_fields(self):
        """TC-10: Verify updating an existing habit modifies its attributes (FR-14, FR-20)."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Read Book', goal='1 time per day')
        update_payload = {
            'name': 'Read 20 Pages',
            'goal': '2 times per day',
            'category': 'Self-care'
        }
        res = self.client.patch(f'/api/habits/{habit.id}/', update_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'Read 20 Pages')
        self.assertEqual(res.data['goal'], '2 times per day')

    # ---------------------------------------------------------
    # 3. CHECK-IN / UNDO CHECK-IN
    # ---------------------------------------------------------
    def test_tc11_habit_check_in_today(self):
        """TC-11: Verify marking a habit complete for today updates status and streak."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Drink 2L Water')
        res = self.client.post(f'/api/habits/{habit.id}/check/', {'date': str(self.today)})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['created'])
        self.assertTrue(res.data['habit']['completed_today'])
        self.assertEqual(res.data['habit']['current_streak'], 1)

    def test_tc12_habit_check_in_idempotency(self):
        """TC-12: Verify duplicate check-in on the same date is idempotent and does not duplicate."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Walk 5000 Steps')
        HabitLog.objects.create(habit=habit, date=self.today)

        res = self.client.post(f'/api/habits/{habit.id}/check/', {'date': str(self.today)})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['created'])
        self.assertEqual(HabitLog.objects.filter(habit=habit, date=self.today).count(), 1)

    def test_tc13_habit_undo_check_in(self):
        """TC-13: Verify undoing a check-in reverts completed status and adjusts streak."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Stretch')
        HabitLog.objects.create(habit=habit, date=self.today)

        res = self.client.delete(f'/api/habits/{habit.id}/check/?date={self.today}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['deleted'])
        self.assertFalse(res.data['habit']['completed_today'])
        self.assertEqual(res.data['habit']['current_streak'], 0)

    # ---------------------------------------------------------
    # 4. STREAK CALCULATION ALGORITHMS (SRS 4.4)
    # ---------------------------------------------------------
    def test_tc14_streak_consecutive_days_ending_today(self):
        """TC-14: Verify 3-day consecutive streak ending today yields current_streak=3."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Deep Work')
        HabitLog.objects.create(habit=habit, date=self.two_days_ago)
        HabitLog.objects.create(habit=habit, date=self.yesterday)
        HabitLog.objects.create(habit=habit, date=self.today)

        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.data['current_streak'], 3)
        self.assertEqual(res.data['longest_streak'], 3)
        self.assertTrue(res.data['completed_today'])

    def test_tc15_streak_maintained_if_done_yesterday_not_today(self):
        """TC-15: Verify streak is preserved if completed yesterday but pending today."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Guitar Practice')
        HabitLog.objects.create(habit=habit, date=self.yesterday)

        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.data['current_streak'], 1)
        self.assertFalse(res.data['completed_today'])

    def test_tc16_streak_resets_when_chain_broken(self):
        """TC-16: Verify streak drops to 0 if neither today nor yesterday was completed."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Floss')
        four_days_ago = self.today - timedelta(days=4)
        HabitLog.objects.create(habit=habit, date=four_days_ago)
        HabitLog.objects.create(habit=habit, date=self.three_days_ago)

        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.data['current_streak'], 0)
        self.assertEqual(res.data['longest_streak'], 2)

    def test_tc17_longest_streak_historical_preservation(self):
        """TC-17: Verify longest streak preserves historical best even after current reset."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Journaling')
        # 4 consecutive days long ago
        for d in range(10, 6, -1):
            HabitLog.objects.create(habit=habit, date=self.today - timedelta(days=d))
        # 1 day completed today
        HabitLog.objects.create(habit=habit, date=self.today)

        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.data['current_streak'], 1)
        self.assertEqual(res.data['longest_streak'], 4)

    # ---------------------------------------------------------
    # 5. INTEGRITY, PROGRESS & ANALYTICS
    # ---------------------------------------------------------
    def test_tc18_habit_deletion_cascade_logs(self):
        """TC-18: Verify deleting a habit cascades and removes all linked HabitLog entries."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Temporary Habit')
        HabitLog.objects.create(habit=habit, date=self.today)
        HabitLog.objects.create(habit=habit, date=self.yesterday)

        res = self.client.delete(f'/api/habits/{habit.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=habit.id).count(), 0)
        self.assertEqual(HabitLog.objects.filter(habit_id=habit.id).count(), 0)

    def test_tc19_daily_progress_percentage_calculation(self):
        """TC-19: Verify daily progress percentage matches completed vs total ratio."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        h1 = Habit.objects.create(user=user, name='Morning Water')
        h2 = Habit.objects.create(user=user, name='Morning Workout')
        h3 = Habit.objects.create(user=user, name='Evening Reading')
        h4 = Habit.objects.create(user=user, name='Night Sleep')

        # Complete 3 of 4 habits today (75%)
        HabitLog.objects.create(habit=h1, date=self.today)
        HabitLog.objects.create(habit=h2, date=self.today)
        HabitLog.objects.create(habit=h3, date=self.today)

        res = self.client.get('/api/habits/stats/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['total_habits'], 4)
        self.assertEqual(res.data['completed_today'], 3)
        self.assertEqual(res.data['today_percentage'], 75)

    def test_tc20_statistics_and_calendar_logs_aggregation(self):
        """TC-20: Verify stats endpoint aggregates calendar check-in dates and weekly summaries."""
        user = User.objects.get_or_create(username='Nachatra')[0]
        habit = Habit.objects.create(user=user, name='Hydration')
        HabitLog.objects.create(habit=habit, date=self.today)
        HabitLog.objects.create(habit=habit, date=self.yesterday)

        res = self.client.get('/api/habits/stats/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(str(self.today), res.data['calendar_data'])
        self.assertIn(str(self.yesterday), res.data['calendar_data'])
        self.assertGreaterEqual(len(res.data['weekly_stats']), 7)
