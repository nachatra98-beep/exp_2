import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  User, List, Bell, Sun, Info, LogOut, Edit2, 
  ChevronRight, Check, Sparkles 
} from 'lucide-react';

export const ProfileView = ({ habits = [], onNavigateToHome }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [appearance, setAppearance] = useState('Light Mode');
  const [showAbout, setShowAbout] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="profile-view-container">
      {/* Profile Header Card */}
      <div className="profile-avatar-section">
        <div className="profile-avatar-wrapper">
          <div className="avatar-circle">
            <User size={54} className="avatar-icon" strokeWidth={1.8} />
          </div>
          <button type="button" className="avatar-edit-badge" title="Change Avatar">
            <Edit2 size={13} strokeWidth={2.5} />
          </button>
        </div>

        <h2 className="profile-user-name">
          {user?.first_name || user?.username || 'Nachatra'}
        </h2>
        <p className="profile-tagline">
          Habit Tracker Enthusiast <Sparkles size={14} className="inline text-amber-500" />
        </p>
      </div>

      {/* Profile Settings Options */}
      <div className="profile-options-list">
        {/* My Habits */}
        <button 
          type="button" 
          className="profile-option-item"
          onClick={onNavigateToHome}
        >
          <div className="option-left">
            <List size={20} className="option-icon" />
            <span className="option-title">My Habits</span>
          </div>
          <span className="option-badge">{habits.length} habits</span>
        </button>

        {/* Notifications */}
        <div className="profile-option-item">
          <div className="option-left">
            <Bell size={20} className="option-icon" />
            <span className="option-title">Notifications</span>
          </div>
          <button
            type="button"
            className={`toggle-switch ${notificationsEnabled ? 'active' : ''}`}
            onClick={() => setNotificationsEnabled(!notificationsEnabled)}
            aria-label="Toggle notifications"
          >
            <div className="toggle-thumb"></div>
          </button>
        </div>

        {/* Appearance */}
        <div className="profile-option-item">
          <div className="option-left">
            <Sun size={20} className="option-icon" />
            <span className="option-title">Appearance</span>
          </div>
          <select
            className="appearance-select"
            value={appearance}
            onChange={(e) => setAppearance(e.target.value)}
          >
            <option value="Light Mode">Light Mode</option>
            <option value="Dark Mode">Dark Mode (v2)</option>
            <option value="System">System</option>
          </select>
        </div>

        {/* About App */}
        <button 
          type="button" 
          className="profile-option-item"
          onClick={() => setShowAbout(!showAbout)}
        >
          <div className="option-left">
            <Info size={20} className="option-icon" />
            <span className="option-title">About App</span>
          </div>
          <ChevronRight size={18} className="text-gray-400" />
        </button>

        {/* About App Details Accordion */}
        {showAbout && (
          <div className="about-app-drawer">
            <p><strong>Habit Tracker v1.0</strong></p>
            <p>Built with ReactJS, Vite, and Django REST Framework according to the SRS specification.</p>
            <p className="text-xs text-amber-700">Small steps. Big changes!</p>
          </div>
        )}

        {/* Logout */}
        <button 
          type="button" 
          className="profile-option-item logout-option"
          onClick={handleLogout}
        >
          <div className="option-left">
            <LogOut size={20} className="logout-icon" />
            <span className="logout-title">Logout</span>
          </div>
        </button>
      </div>
    </div>
  );
};
