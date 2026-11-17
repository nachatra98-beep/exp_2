import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, BarChart2, Plus, Calendar, User } from 'lucide-react';

export const BottomNav = ({ activeTab = 'home', onTabChange }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavClick = (tabKey) => {
    if (tabKey === 'add') {
      navigate('/add');
      return;
    }

    if (location.pathname !== '/home') {
      navigate(`/home?tab=${tabKey}`);
    } else if (onTabChange) {
      onTabChange(tabKey);
    }
  };

  return (
    <nav className="bottom-nav-container">
      <div className="bottom-nav-bar">
        {/* Home */}
        <button
          type="button"
          className={`nav-item ${activeTab === 'home' && location.pathname === '/home' ? 'active' : ''}`}
          onClick={() => handleNavClick('home')}
        >
          <Home size={22} strokeWidth={activeTab === 'home' ? 2.5 : 2} />
          <span className="nav-label">Home</span>
        </button>

        {/* Stats */}
        <button
          type="button"
          className={`nav-item ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => handleNavClick('stats')}
        >
          <BarChart2 size={22} strokeWidth={activeTab === 'stats' ? 2.5 : 2} />
          <span className="nav-label">Stats</span>
        </button>

        {/* Floating Add Button */}
        <div className="nav-add-wrapper">
          <button
            type="button"
            className="floating-add-btn"
            onClick={() => navigate('/add')}
            title="Add New Habit"
            aria-label="Add Habit"
          >
            <Plus size={28} strokeWidth={2.8} />
          </button>
        </div>

        {/* Calendar */}
        <button
          type="button"
          className={`nav-item ${activeTab === 'calendar' ? 'active' : ''}`}
          onClick={() => handleNavClick('calendar')}
        >
          <Calendar size={22} strokeWidth={activeTab === 'calendar' ? 2.5 : 2} />
          <span className="nav-label">Calendar</span>
        </button>

        {/* Profile */}
        <button
          type="button"
          className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => handleNavClick('profile')}
        >
          <User size={22} strokeWidth={activeTab === 'profile' ? 2.5 : 2} />
          <span className="nav-label">Profile</span>
        </button>
      </div>
    </nav>
  );
};
