import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Check, Edit3, Trash2, BookOpen, Droplet, Dumbbell, Moon, 
  Sparkles, Heart, Coffee, Bike, Music, Flame
} from 'lucide-react';
import confetti from 'canvas-confetti';

const ICON_MAP = {
  book: BookOpen,
  water: Droplet,
  exercise: Dumbbell,
  moon: Moon,
  sparkles: Sparkles,
  heart: Heart,
  coffee: Coffee,
  bike: Bike,
  music: Music,
};

export const HabitCard = ({ habit, onToggleCheck, onDelete }) => {
  const navigate = useNavigate();
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [submittingCheck, setSubmittingCheck] = useState(false);

  const IconComponent = ICON_MAP[habit.icon] || BookOpen;

  const handleCheck = async (e) => {
    e.stopPropagation();
    if (submittingCheck) return;
    setSubmittingCheck(true);

    // If marking complete, burst confetti!
    if (!habit.completed_today) {
      confetti({
        particleCount: 40,
        spread: 60,
        origin: { y: 0.7 },
        colors: ['#F59E0B', '#FBBF24', '#FCD34D', '#10B981']
      });
    }

    try {
      await onToggleCheck(habit.id, !habit.completed_today);
    } finally {
      setSubmittingCheck(false);
    }
  };

  const handleDelete = async (e) => {
    e.stopPropagation();
    setIsDeleting(true);
    try {
      await onDelete(habit.id);
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  return (
    <div className={`habit-card ${habit.completed_today ? 'completed' : ''}`}>
      <div className="habit-card-main">
        {/* Habit Icon Container */}
        <div 
          className="habit-icon-wrapper" 
          style={{ backgroundColor: `${habit.color || '#F59E0B'}22`, color: habit.color || '#D97706' }}
        >
          <IconComponent size={24} strokeWidth={2.2} />
        </div>

        {/* Habit Details */}
        <div className="habit-info">
          <div className="habit-header-row">
            <h3 className="habit-name">{habit.name}</h3>
            {habit.current_streak > 0 && (
              <span className="habit-streak-badge" title={`Current: ${habit.current_streak} days, Longest: ${habit.longest_streak} days`}>
                <Flame size={13} className="text-amber-500 fill-amber-500" />
                <span>{habit.current_streak}d</span>
              </span>
            )}
          </div>
          
          <p className="habit-subtitle">
            {habit.frequency || 'Daily'} • Goal: {habit.goal || '1 time'}
            {habit.description && <span className="habit-desc-text"> — {habit.description}</span>}
          </p>
        </div>

        {/* Action icons (Edit & Delete) */}
        <div className="habit-actions">
          <button 
            type="button" 
            className="action-btn edit-btn" 
            title="Edit habit"
            onClick={() => navigate(`/add?id=${habit.id}`)}
          >
            <Edit3 size={16} />
          </button>
          
          <button 
            type="button" 
            className="action-btn delete-btn" 
            title="Delete habit"
            onClick={() => setShowConfirm(true)}
          >
            <Trash2 size={16} />
          </button>

          {/* Toggle Check Button */}
          <button
            type="button"
            className={`check-btn ${habit.completed_today ? 'checked' : 'unchecked'}`}
            onClick={handleCheck}
            disabled={submittingCheck}
            title={habit.completed_today ? "Completed today (click to undo)" : "Click to mark as done today"}
            aria-label={`Mark ${habit.name} as ${habit.completed_today ? 'incomplete' : 'complete'}`}
          >
            {habit.completed_today && <Check size={18} strokeWidth={3} color="#FFFFFF" />}
          </button>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {showConfirm && (
        <div className="confirm-delete-overlay">
          <div className="confirm-delete-box">
            <p>Delete "<strong>{habit.name}</strong>"?</p>
            <div className="confirm-actions">
              <button 
                type="button" 
                className="btn-cancel-delete" 
                onClick={() => setShowConfirm(false)}
              >
                Cancel
              </button>
              <button 
                type="button" 
                className="btn-confirm-delete" 
                disabled={isDeleting}
                onClick={handleDelete}
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
