import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../api/client';
import { 
  ArrowLeft, Edit2, Target, Calendar as CalendarIcon, Clock, 
  Palette, Tag, FileText, Check, AlertCircle, BookOpen, Droplet, 
  Dumbbell, Moon, Sparkles, Heart, Coffee, Bike, Music
} from 'lucide-react';

const CATEGORIES = ['General', 'Study', 'Health', 'Fitness', 'Productivity', 'Mindfulness'];
const FREQUENCIES = ['Daily', 'Weekdays', 'Weekends', '3 times a week'];
const GOALS = ['1 time per day', '2 times per day', '3 times per day', 'Custom'];
const COLOR_PRESETS = [
  '#F59E0B', // Amber / Gold
  '#3B82F6', // Blue
  '#10B981', // Emerald Green
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#F97316', // Orange
];

const ICONS = [
  { key: 'book', label: 'Study / Read', icon: BookOpen },
  { key: 'water', label: 'Drink Water', icon: Droplet },
  { key: 'exercise', label: 'Exercise', icon: Dumbbell },
  { key: 'moon', label: 'Sleep Early', icon: Moon },
  { key: 'sparkles', label: 'Mindset', icon: Sparkles },
  { key: 'heart', label: 'Health', icon: Heart },
  { key: 'coffee', label: 'Break', icon: Coffee },
  { key: 'bike', label: 'Cycling', icon: Bike },
  { key: 'music', label: 'Hobbies', icon: Music },
];

export const AddHabit = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editId = searchParams.get('id');
  const isEditing = Boolean(editId);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('General');
  const [frequency, setFrequency] = useState('Daily');
  const [goal, setGoal] = useState('1 time per day');
  const [color, setColor] = useState('#F59E0B');
  const [icon, setIcon] = useState('book');
  const [reminderTime, setReminderTime] = useState('');

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Load existing habit if editing (FR-20)
  useEffect(() => {
    if (isEditing) {
      setLoading(true);
      api.get(`/api/habits/${editId}/`)
        .then((res) => {
          const habit = res.data;
          setName(habit.name || '');
          setDescription(habit.description || '');
          setCategory(habit.category || 'General');
          setFrequency(habit.frequency || 'Daily');
          setGoal(habit.goal || '1 time per day');
          setColor(habit.color || '#F59E0B');
          setIcon(habit.icon || 'book');
          setReminderTime(habit.reminder_time ? habit.reminder_time.slice(0, 5) : '');
        })
        .catch(() => {
          setErrorMsg('Failed to load habit details.');
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [editId, isEditing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!name.trim()) {
      setErrorMsg('Habit name is required.');
      return;
    }

    if (name.length > 100) {
      setErrorMsg('Habit name must be 100 characters or fewer.');
      return;
    }

    if (description && description.length > 255) {
      setErrorMsg('Description must be 255 characters or fewer.');
      return;
    }

    const payload = {
      name: name.trim(),
      description: description.trim(),
      category,
      frequency,
      goal,
      color,
      icon,
      reminder_time: reminderTime ? `${reminderTime}:00` : null,
    };

    setSubmitting(true);
    try {
      if (isEditing) {
        await api.put(`/api/habits/${editId}/`, payload);
      } else {
        await api.post('/api/habits/', payload);
      }
      navigate('/home');
    } catch (err) {
      let msg = err.response?.data?.detail;
      if (!msg && err.response?.data?.errors) {
        const errors = err.response.data.errors;
        const firstKey = Object.keys(errors)[0];
        msg = Array.isArray(errors[firstKey]) ? errors[firstKey][0] : errors[firstKey];
      }
      setErrorMsg(msg || 'Failed to save habit. Please check your inputs.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="add-habit-page">
      <div className="app-shell-container">
        {/* Top Header */}
        <header className="page-header">
          <button 
            type="button" 
            className="back-btn" 
            onClick={() => navigate('/home')}
            aria-label="Back to Home"
          >
            <ArrowLeft size={22} />
          </button>
          <h1 className="header-title">{isEditing ? 'Edit Habit' : 'Add Habit'}</h1>
          <div className="header-placeholder-space"></div>
        </header>

        {/* Cute Clipboard Illustration Hero */}
        <div className="clipboard-hero">
          <div className="clipboard-icon-card">
            <div className="clipboard-clip"></div>
            <div className="clipboard-paper">
              <div className="clipboard-line line-check">
                <span className="chk-icon">✓</span>
                <span className="bar"></span>
              </div>
              <div className="clipboard-line line-check">
                <span className="chk-icon">✓</span>
                <span className="bar"></span>
              </div>
              <div className="clipboard-line line-check">
                <span className="chk-icon">✓</span>
                <span className="bar"></span>
              </div>
            </div>
          </div>
          <div className="hero-sparkle-dot dot-1"></div>
          <div className="hero-sparkle-dot dot-2"></div>
        </div>

        {/* Error message alert */}
        {errorMsg && (
          <div className="form-error-alert" role="alert">
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        {loading ? (
          <div className="loading-spinner-box">
            <div className="spinner"></div>
            <p>Loading habit data...</p>
          </div>
        ) : (
          /* Habit Form */
          <form onSubmit={handleSubmit} className="habit-form">
            {/* Habit Name */}
            <div className="form-section">
              <label htmlFor="habitName" className="section-label">
                <Edit2 size={16} />
                <span>Habit Name</span>
              </label>
              <div className="input-box">
                <input
                  id="habitName"
                  type="text"
                  placeholder="e.g. Read a book"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  maxLength={100}
                  required
                />
              </div>
            </div>

            {/* Frequency Dropdown */}
            <div className="form-section">
              <label htmlFor="frequency" className="section-label">
                <CalendarIcon size={16} />
                <span>Frequency</span>
              </label>
              <div className="select-box">
                <select
                  id="frequency"
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                >
                  {FREQUENCIES.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Goal Dropdown */}
            <div className="form-section">
              <label htmlFor="goal" className="section-label">
                <Target size={16} />
                <span>Goal</span>
              </label>
              <div className="select-box">
                <select
                  id="goal"
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                >
                  {GOALS.map((g) => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Category Dropdown */}
            <div className="form-section">
              <label htmlFor="category" className="section-label">
                <Tag size={16} />
                <span>Category</span>
              </label>
              <div className="select-box">
                <select
                  id="category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Icon Picker */}
            <div className="form-section">
              <label className="section-label">
                <Sparkles size={16} />
                <span>Icon</span>
              </label>
              <div className="icon-selector-grid">
                {ICONS.map((item) => {
                  const ItemIcon = item.icon;
                  return (
                    <button
                      key={item.key}
                      type="button"
                      className={`icon-option-btn ${icon === item.key ? 'selected' : ''}`}
                      onClick={() => setIcon(item.key)}
                      title={item.label}
                    >
                      <ItemIcon size={20} />
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Color Palette */}
            <div className="form-section">
              <label className="section-label">
                <Palette size={16} />
                <span>Theme Color</span>
              </label>
              <div className="color-palette-row">
                {COLOR_PRESETS.map((hex) => (
                  <button
                    key={hex}
                    type="button"
                    className={`color-swatch-btn ${color === hex ? 'selected' : ''}`}
                    style={{ backgroundColor: hex }}
                    onClick={() => setColor(hex)}
                  >
                    {color === hex && <Check size={14} color="#FFF" strokeWidth={3} />}
                  </button>
                ))}
              </div>
            </div>

            {/* Reminder Time (Optional) */}
            <div className="form-section">
              <label htmlFor="reminder" className="section-label">
                <Clock size={16} />
                <span>Reminder Time (Optional)</span>
              </label>
              <div className="input-box">
                <input
                  id="reminder"
                  type="time"
                  value={reminderTime}
                  onChange={(e) => setReminderTime(e.target.value)}
                />
              </div>
            </div>

            {/* Description (Optional) */}
            <div className="form-section">
              <label htmlFor="description" className="section-label">
                <FileText size={16} />
                <span>Description (Optional)</span>
              </label>
              <div className="textarea-box">
                <textarea
                  id="description"
                  rows={2}
                  placeholder="Notes or extra motivation for this habit..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  maxLength={255}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="form-submit-row">
              <button
                type="submit"
                className="btn-primary-yellow"
                disabled={submitting}
              >
                {submitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Add Habit'}
              </button>
              
              <button
                type="button"
                className="btn-cancel"
                onClick={() => navigate('/home')}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
