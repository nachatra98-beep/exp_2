import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Eye, EyeOff, Sparkles, CheckCircle2, Lock, User, Mail, ArrowRight } from 'lucide-react';

export const Login = () => {
  const { login, register, isAuthenticated, authError, setAuthError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [isRegister, setIsRegister] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form states
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [clientError, setClientError] = useState('');

  // If already logged in, redirect to /home (FR-6)
  useEffect(() => {
    if (isAuthenticated) {
      const destination = location.state?.from?.pathname || '/home';
      navigate(destination, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setClientError('');
    setAuthError(null);

    // Frontend validations (FR-5)
    if (!username.trim()) {
      setClientError('Please enter your username.');
      return;
    }

    if (!password) {
      setClientError('Please enter your password.');
      return;
    }

    if (password.length < 8) {
      setClientError('Password must be at least 8 characters long.');
      return;
    }

    if (isRegister) {
      if (!email.trim()) {
        setClientError('Please enter your email address.');
        return;
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        setClientError('Please enter a valid email address.');
        return;
      }
      if (password !== confirmPassword) {
        setClientError('Passwords do not match.');
        return;
      }

      setSubmitting(true);
      const result = await register(username.trim(), email.trim(), password);
      setSubmitting(false);
      if (result.success) {
        navigate('/home', { replace: true });
      }
    } else {
      setSubmitting(true);
      const result = await login(username.trim(), password);
      setSubmitting(false);
      if (result.success) {
        navigate('/home', { replace: true });
      }
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-card">
        {/* Header with App Logo & Title */}
        <div className="login-header">
          <div className="login-logo-badge">
            <span className="logo-emoji">💛</span>
          </div>
          <h1 className="login-title">Habit Tracker</h1>
          <p className="login-subtitle">Small steps. Big changes!</p>
        </div>

        {/* Tab Toggle */}
        <div className="auth-toggle-bar">
          <button
            type="button"
            className={`auth-toggle-btn ${!isRegister ? 'active' : ''}`}
            onClick={() => {
              setIsRegister(false);
              setClientError('');
              setAuthError(null);
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`auth-toggle-btn ${isRegister ? 'active' : ''}`}
            onClick={() => {
              setIsRegister(true);
              setClientError('');
              setAuthError(null);
            }}
          >
            Create Account
          </button>
        </div>

        {/* Alerts / Error display */}
        {(clientError || authError) && (
          <div className="auth-error-alert" role="alert">
            <span>{clientError || authError}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          {/* Username */}
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <div className="input-with-icon">
              <User size={18} className="input-icon" />
              <input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </div>
          </div>

          {/* Email (only on register) */}
          {isRegister && (
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <div className="input-with-icon">
                <Mail size={18} className="input-icon" />
                <input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </div>
            </div>
          )}

          {/* Password */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock size={18} className="input-icon" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                required
              />
              <button
                type="button"
                className="btn-toggle-password"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {/* Confirm Password (only on register) */}
          {isRegister && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <div className="input-with-icon">
                <Lock size={18} className="input-icon" />
                <input
                  id="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  autoComplete="new-password"
                  required
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className="btn-auth-primary"
            disabled={submitting}
          >
            {submitting ? (
              'Please wait...'
            ) : isRegister ? (
              <>
                <span>Sign Up</span>
                <ArrowRight size={18} />
              </>
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        {/* Toggle between register & login */}
        <div className="login-footer">
          {isRegister ? (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                className="link-switch-auth"
                onClick={() => {
                  setIsRegister(false);
                  setClientError('');
                  setAuthError(null);
                }}
              >
                Sign in
              </button>
            </p>
          ) : (
            <p>
              New here?{' '}
              <button
                type="button"
                className="link-switch-auth"
                onClick={() => {
                  setIsRegister(true);
                  setClientError('');
                  setAuthError(null);
                }}
              >
                Create an account
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
