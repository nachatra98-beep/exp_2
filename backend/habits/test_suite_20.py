from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import Habit, HabitLog

class Application20Tests(TestCase):
    """
    Comprehensive 20-Test Suite for Habit Tracker Web Application.
    Covers Authentication, Habit CRUD, Validation, Check-in / Undo,
    Streak Logic, Integrity, and Analytics.
    """

    def setUp(self):
        self.client = APIClient()
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.two_days_ago = self.today - timedelta(days=2)
        self.three_days_ago = self.today - timedelta(days=3)

        # Standard test user
        self.user = User.objects.create_user(
            username='qa_nachatra',
            email='nachatra@test.com',
            password='Password123!'
        )
        self.client.force_authenticate(user=self.user)

    # ---------------------------------------------------------
    # 1. AUTHENTICATION & REGISTRATION
    # ---------------------------------------------------------
    def test_tc01_user_registration_valid(self):
        """TC-01: Verify successful user registration with valid credentials."""
        self.client.logout()
        payload = {
            'username': 'newuser_alex',
            'email': 'alex@example.com',
            'password': 'SecurePassword2026!'
        }
        res = self.client.post('/api/auth/register/', payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.data['user']['username'], 'newuser_alex')

    def test_tc02_user_registration_password_too_short(self):
        """TC-02: Verify registration fails when password is shorter than 8 characters."""
        self.client.logout()
        payload = {
            'username': 'short_pass_user',
            'email': 'short@example.com',
            'password': 'abc'
        }
        res = self.client.post('/api/auth/register/', payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('errors', res.data)
        self.assertIn('password', res.data['errors'])

    def test_tc03_user_registration_duplicate_email(self):
        """TC-03: Verify registration rejects an already registered email."""
        self.client.logout()
        payload = {
            'username': 'another_user',
            'email': 'nachatra@test.com',  # Already exists in setUp
            'password': 'Password123!'
        }
        res = self.client.post('/api/auth/register/', payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data['errors'])

    def test_tc04_user_login_valid_credentials(self):
        """TC-04: Verify login returns JWT access and refresh tokens for valid credentials."""
        self.client.logout()
        payload = {
            'username': 'qa_nachatra',
            'password': 'Password123!'
        }
        res = self.client.post('/api/auth/login/', payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_tc05_user_login_invalid_credentials_generic_message(self):
        """TC-05: Verify login fails with a generic error on incorrect credentials (FR-4)."""
        self.client.logout()
        payload = {
            'username': 'qa_nachatra',
            'password': 'IncorrectPassword!'
        }
        res = self.client.post('/api/auth/login/', payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', res.data)
        self.assertEqual(res.data['detail'], 'Invalid username or password.')

    def test_tc06_jwt_token_refresh(self):
        """TC-06: Verify refresh endpoint issues a new valid access token."""
        self.client.logout()
        login_res = self.client.post('/api/auth/login/', {
            'username': 'qa_nachatra',
            'password': 'Password123!'
        })
        refresh_token = login_res.data['refresh']

        ref_res = self.client.post('/api/auth/refresh/', {'refresh': refresh_token})
        self.assertEqual(ref_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', ref_res.data)

    # ---------------------------------------------------------
    # 2. HABIT MANAGEMENT (CRUD)
    # ---------------------------------------------------------
    def test_tc07_habit_creation_standard(self):
        """TC-07: Verify creating a habit stores all fields and initializes streaks to 0."""
        payload = {
            'name': 'Study for 1 hour',
            'description': 'Daily coding and algorithms',
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

    def test_tc08_habit_creation_name_required(self):
        """TC-08: Verify habit creation fails when name is empty or missing."""
        payload = {
            'name': '   ',
            'category': 'Health'
        }
        res = self.client.post('/api/habits/', payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data['errors'])

    def test_tc09_habit_creation_duplicate_name_rejected(self):
        """TC-09: Verify creating a duplicate habit name for the same user is rejected (FR-22)."""
        Habit.objects.create(user=self.user, name='Drink 2L Water')
        res = self.client.post('/api/habits/', {'name': 'Drink 2L Water'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data['errors'])

    def test_tc10_habit_list_retrieval(self):
        """TC-10: Verify habit listing retrieves active habits with accurate computed fields."""
        Habit.objects.create(user=self.user, name='Exercise')
        Habit.objects.create(user=self.user, name='Sleep Early')

        res = self.client.get('/api/habits/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        habit_names = [h['name'] for h in res.data]
        self.assertIn('Exercise', habit_names)
        self.assertIn('Sleep Early', habit_names)

    def test_tc11_habit_single_detail_retrieval(self):
        """TC-11: Verify retrieving a single habit by ID."""
        habit = Habit.objects.create(user=self.user, name='Meditation', category='Mindfulness')
        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], habit.id)
        self.assertEqual(res.data['name'], 'Meditation')

    def test_tc12_habit_update_fields(self):
        """TC-12: Verify updating an existing habit modifies its attributes (FR-14, FR-20)."""
        habit = Habit.objects.create(user=self.user, name='Read Book', goal='1 time per day')
        update_payload = {
            'name': 'Read 20 Pages',
            'goal': '2 times per day',
            'category': 'Self-care'
        }
        res = self.client.patch(f'/api/habits/{habit.id}/', update_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'Read 20 Pages')
        self.assertEqual(res.data['goal'], '2 times per day')
        self.assertEqual(res.data['category'], 'Self-care')

    # ---------------------------------------------------------
    # 3. CHECK-IN / UNDO CHECK-IN
    # ---------------------------------------------------------
    def test_tc13_habit_check_in_today(self):
        """TC-13: Verify marking a habit complete for today updates status and streak."""
        habit = Habit.objects.create(user=self.user, name='Drink 2L Water')
        res = self.client.post(f'/api/habits/{habit.id}/check/', {'date': str(self.today)})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data['created'])
        self.assertTrue(res.data['habit']['completed_today'])
        self.assertEqual(res.data['habit']['current_streak'], 1)

    def test_tc14_habit_check_in_idempotency(self):
        """TC-14: Verify duplicate check-in on the same date is idempotent and does not duplicate."""
        habit = Habit.objects.create(user=self.user, name='Walk 5000 Steps')
        HabitLog.objects.create(habit=habit, date=self.today)

        # Attempt second check-in for the same date
        res = self.client.post(f'/api/habits/{habit.id}/check/', {'date': str(self.today)})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['created'])
        self.assertEqual(HabitLog.objects.filter(habit=habit, date=self.today).count(), 1)

    def test_tc15_habit_undo_check_in(self):
        """TC-15: Verify undoing a check-in reverts completed status and adjusts streak."""
        habit = Habit.objects.create(user=self.user, name='Stretch')
        HabitLog.objects.create(habit=habit, date=self.today)

        res = self.client.delete(f'/api/habits/{habit.id}/check/?date={self.today}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['deleted'])
        self.assertFalse(res.data['habit']['completed_today'])
        self.assertEqual(res.data['habit']['current_streak'], 0)

    # ---------------------------------------------------------
    # 4. STREAK CALCULATION ALGORITHMS (SRS 4.4)
    # ---------------------------------------------------------
    def test_tc16_streak_consecutive_days_ending_today(self):
        """TC-16: Verify 3-day consecutive streak ending today yields current_streak=3."""
        habit = Habit.objects.create(user=self.user, name='Deep Work')
        HabitLog.objects.create(habit=habit, date=self.two_days_ago)
        HabitLog.objects.create(habit=habit, date=self.yesterday)
        HabitLog.objects.create(habit=habit, date=self.today)

        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.data['current_streak'], 3)
        self.assertEqual(res.data['longest_streak'], 3)
        self.assertTrue(res.data['completed_today'])

    def test_tc17_streak_maintained_if_done_yesterday_not_today(self):
        """TC-17: Verify streak is preserved if completed yesterday but pending today."""
        habit = Habit.objects.create(user=self.user, name='Guitar Practice')
        HabitLog.objects.create(habit=habit, date=self.yesterday)

        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.data['current_streak'], 1)
        self.assertFalse(res.data['completed_today'])

    def test_tc18_streak_resets_when_chain_broken(self):
        """TC-18: Verify streak drops to 0 if neither today nor yesterday was completed."""
        habit = Habit.objects.create(user=self.user, name='Floss')
        # Check-ins 2 and 3 days ago, but missed yesterday and today
        four_days_ago = self.today - timedelta(days=4)
        HabitLog.objects.create(habit=habit, date=four_days_ago)
        HabitLog.objects.create(habit=habit, date=self.three_days_ago)

        res = self.client.get(f'/api/habits/{habit.id}/')
        self.assertEqual(res.data['current_streak'], 0)
        self.assertEqual(res.data['longest_streak'], 2)

    # ---------------------------------------------------------
    # 5. INTEGRITY & ANALYTICS
    # ---------------------------------------------------------
    def test_tc19_habit_deletion_cascade_logs(self):
        """TC-19: Verify deleting a habit cascades and removes its HabitLog entries."""
        habit = Habit.objects.create(user=self.user, name='Temporary Habit')
        HabitLog.objects.create(habit=habit, date=self.today)
        HabitLog.objects.create(habit=habit, date=self.yesterday)

        res = self.client.delete(f'/api/habits/{habit.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=habit.id).count(), 0)
        self.assertEqual(HabitLog.objects.filter(habit_id=habit.id).count(), 0)

    def test_tc20_statistics_aggregation_metrics(self):
        """TC-20: Verify /api/habits/stats/ calculates completion rates, streak, and calendar logs."""
        h1 = Habit.objects.create(user=self.user, name='Habit One')
        h2 = Habit.objects.create(user=self.user, name='Habit Two')
        # Complete h1 today, leave h2 incomplete
        HabitLog.objects.create(habit=h1, date=self.today)

        res = self.client.get('/api/habits/stats/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['total_habits'], 2)
        self.assertEqual(res.data['completed_today'], 1)
        self.assertEqual(res.data['today_percentage'], 50)  # 1 out of 2 = 50%
        self.assertIn(str(self.today), res.data['calendar_data'])
        self.assertGreaterEqual(len(res.data['weekly_stats']), 7)
