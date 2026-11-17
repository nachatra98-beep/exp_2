import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api, { getLocalDateString } from '../api/client';
import { StreakBanner } from '../components/StreakBanner';
import { ProgressBar } from '../components/ProgressBar';
import { HabitCard } from '../components/HabitCard';
import { BottomNav } from '../components/BottomNav';
import { CalendarView } from './CalendarView';
import { StatsView } from './StatsView';
import { ProfileView } from './ProfileView';
import { 
  Plus, Settings, ArrowLeft, RefreshCw, 
  AlertCircle, Sparkles, Calendar as CalendarIcon, ArrowRight 
} from 'lucide-react';

export const Home = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const activeTab = searchParams.get('tab') || 'home';

  const [habits, setHabits] = useState([]);
  const [stats, setStats] = useState({
    total_habits: 0,
    completed_today: 0,
    today_percentage: 0,
    current_streak: 0,
    longest_streak: 0,
    total_completions: 0,
    calendar_data: {},
  });
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Formatted date string for FR-9
  const todayFormatted = new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(new Date());

  const fetchHabitsAndStats = async () => {
    try {
      const [habitsRes, statsRes] = await Promise.all([
        api.get('/api/habits/'),
        api.get('/api/habits/stats/')
      ]);
      setHabits(habitsRes.data);
      setStats(statsRes.data);
      setErrorMsg('');
    } catch (err) {
      setErrorMsg('Failed to load habits. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHabitsAndStats();
  }, []);

  const handleTabChange = (newTab) => {
    if (newTab === 'home') {
      searchParams.delete('tab');
      setSearchParams(searchParams);
    } else {
      setSearchParams({ tab: newTab });
    }
  };

  // Check / Uncheck habit for today (FR-11)
  const handleToggleCheck = async (habitId, markComplete) => {
    // Optimistic update
    setHabits(prev => prev.map(h => {
      if (h.id === habitId) {
        const nextComplete = markComplete;
        const streakChange = nextComplete ? 1 : (h.current_streak > 0 ? -1 : 0);
        return {
          ...h,
          completed_today: nextComplete,
          current_streak: Math.max(0, h.current_streak + streakChange)
        };
      }
      return h;
    }));

    try {
      if (markComplete) {
        await api.post(`/api/habits/${habitId}/check/`, { date: getLocalDateString() });
      } else {
        await api.delete(`/api/habits/${habitId}/check/?date=${getLocalDateString()}`);
      }
      // Refresh to get server-calculated exact streaks and stats
      fetchHabitsAndStats();
    } catch (err) {
      // Revert on error
      fetchHabitsAndStats();
      setErrorMsg('Could not update habit status. Please retry.');
    }
  };

  // Delete habit (FR-14)
  const handleDeleteHabit = async (habitId) => {
    try {
      await api.delete(`/api/habits/${habitId}/`);
      setHabits(prev => prev.filter(h => h.id !== habitId));
      fetchHabitsAndStats();
    } catch (err) {
      setErrorMsg('Failed to delete habit.');
    }
  };

  const completedCount = habits.filter(h => h.completed_today).length;
  const bestStreak = stats.current_streak || (habits.length > 0 ? Math.max(...habits.map(h => h.current_streak), 0) : 0);

  return (
    <div className="home-page-container">
      <div className="app-shell-container">
        {/* Dynamic Header depending on Active Tab */}
        {activeTab === 'home' ? (
          <header className="home-header">
            <div className="user-greeting-box">
              <h1 className="greeting-title">
                Hello, {user?.first_name || user?.username || 'Nachatra'} <span className="heart-icon">💛</span>
              </h1>
              <p className="greeting-subtitle">Small steps. Big changes!</p>
              <div className="date-badge">
                <CalendarIcon size={12} className="inline mr-1" />
                <span>{todayFormatted}</span>
              </div>
            </div>

            <div className="header-actions">
              <button
                type="button"
                className="header-icon-btn"
                title="Profile & Settings"
                onClick={() => handleTabChange('profile')}
              >
                <Settings size={22} />
              </button>
            </div>
          </header>
        ) : (
          <header className="subpage-header">
            <button
              type="button"
              className="back-btn"
              onClick={() => handleTabChange('home')}
              aria-label="Back to Home"
            >
              <ArrowLeft size={22} />
            </button>
            <h1 className="header-title">
              {activeTab === 'stats' && 'Statistics'}
              {activeTab === 'calendar' && 'Calendar'}
              {activeTab === 'profile' && 'Profile'}
            </h1>
            <div className="header-placeholder-space"></div>
          </header>
        )}

        {/* Global Error Banner if any */}
        {errorMsg && (
          <div className="global-error-alert" role="alert">
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'stats' ? (
          <StatsView
            habits={habits}
            stats={stats}
            onBackToHome={() => handleTabChange('home')}
          />
        ) : activeTab === 'calendar' ? (
          <CalendarView
            habits={habits}
            stats={stats}
            onBackToHome={() => handleTabChange('home')}
          />
        ) : activeTab === 'profile' ? (
          <ProfileView
            habits={habits}
            onNavigateToHome={() => handleTabChange('home')}
          />
        ) : (
          /* Main Dashboard Content (Home) */
          <main className="dashboard-content">
            {/* Trophy Streak Banner (as shown in image) */}
            <StreakBanner 
              streak={bestStreak || 7} 
              totalCompleted={stats.total_completions || 21} 
            />

            {/* My Habits Section Header */}
            <div className="section-header-row">
              <h2 className="section-heading">My Habits</h2>
              <div className="section-actions-right">
                <button
                  type="button"
                  className="link-view-all"
                  onClick={() => handleTabChange('calendar')}
                >
                  <span>View All</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>

            {/* Loading State */}
            {loading ? (
              <div className="loading-state-box">
                <div className="spinner"></div>
                <p>Loading your habits...</p>
              </div>
            ) : habits.length === 0 ? (
              /* Empty State (FR-16) */
              <div className="empty-habits-box">
                <div className="empty-sparkle-icon">
                  <Sparkles size={36} className="text-amber-500" />
                </div>
                <h3>No habits yet!</h3>
                <p>Start tracking your daily routines by creating your first habit.</p>
                <button
                  type="button"
                  className="btn-create-first"
                  onClick={() => navigate('/add')}
                >
                  <Plus size={18} />
                  <span>Add Your First Habit</span>
                </button>
              </div>
            ) : (
              /* Habit Cards List (FR-10, FR-11, FR-13, FR-14) */
              <div className="habits-list-grid">
                {habits.map((habit) => (
                  <HabitCard
                    key={habit.id}
                    habit={habit}
                    onToggleCheck={handleToggleCheck}
                    onDelete={handleDeleteHabit}
                  />
                ))}
              </div>
            )}

            {/* "Your Progress" Card (FR-12 & UI Mockup) */}
            {habits.length > 0 && (
              <ProgressBar
                completedCount={completedCount}
                totalCount={habits.length}
              />
            )}
          </main>
        )}

        {/* Bottom Navigation Bar */}
        <BottomNav
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />
      </div>
    </div>
  );
};
