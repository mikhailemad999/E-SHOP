/**
 * RegisterPage — Universal multi-role self-registration.
 * Allows creating Buyer, Seller, Delivery Manager, Delivery Agent, Admin, or Super Admin accounts.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Phone, Building2, Shield, Truck, Crown } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Input from '../../components/atoms/Input';
import './AuthPages.css';

const ROLES = [
  { id: 'customer', label: 'Buyer / Customer', icon: User },
  { id: 'seller', label: 'Seller Store', icon: Building2 },
  { id: 'delivery_manager', label: 'Delivery Manager', icon: Truck },
  { id: 'delivery_agent', label: 'Delivery Agent', icon: Truck },
  { id: 'admin', label: 'System Admin', icon: Shield },
  { id: 'super_admin', label: 'Super Admin', icon: Crown },
];

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [role, setRole] = useState('customer');
  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    password: '',
    password_confirm: '',
    business_name: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setErrors({ ...errors, [e.target.name]: '' });
    setApiError('');
  };

  const validate = () => {
    const e = {};
    if (!form.username) e.username = 'Username is required';
    if (!form.email) e.email = 'Email is required';
    if (!form.password) e.password = 'Password is required';
    else if (form.password.length < 8) e.password = 'Must be at least 8 characters';
    if (form.password !== form.password_confirm) e.password_confirm = 'Passwords do not match';
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const getTargetDashboard = (roleStr) => {
    switch (roleStr) {
      case 'super_admin':
      case 'admin':
        return '/admin';
      case 'seller':
        return '/seller';
      case 'delivery_manager':
        return '/delivery';
      case 'delivery_agent':
        return '/delivery/agent';
      default:
        return '/';
    }
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setApiError('');

    try {
      // POST to Universal Registration endpoint
      await api.post('/auth/register/', { ...form, role });
      
      // Perform immediate login to establish session
      const loginSuccess = await login(form.username, form.password);

      if (loginSuccess) {
        navigate(getTargetDashboard(role));
      } else {
        navigate('/login');
      }
    } catch (err) {
      console.error('Registration API Error:', err);
      const detail = err.response?.data;
      if (typeof detail === 'object' && detail !== null) {
        const fieldErrors = {};
        Object.entries(detail).forEach(([key, val]) => {
          fieldErrors[key] = Array.isArray(val) ? val[0] : val;
        });
        setErrors(fieldErrors);
      } else {
        setApiError('Registration failed. Please verify your fields.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-page__card auth-page__card--wide animate-fade-in-up">
        <div className="auth-page__header">
          <Link to="/" className="auth-page__logo">
            <span className="auth-page__logo-icon">◆</span>
            <span className="auth-page__logo-text">E-Shop</span>
          </Link>
          <h1 className="auth-page__title">Create Your Account</h1>
          <p className="auth-page__subtitle">Select your account type to register in the database</p>
        </div>

        {/* Multi-Role Selector */}
        <div className="auth-page__role-selector" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '20px' }}>
          {ROLES.map((r) => {
            const Icon = r.icon;
            const isActive = role === r.id;
            return (
              <button
                key={r.id}
                type="button"
                className={`auth-page__role-btn ${isActive ? 'auth-page__role-btn--active' : ''}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '10px',
                  borderRadius: '8px',
                  border: isActive ? '2px solid var(--eshop-primary-600)' : '1px solid #e2e8f0',
                  background: isActive ? 'var(--eshop-primary-50)' : '#ffffff',
                  color: isActive ? 'var(--eshop-primary-700)' : '#475569',
                  fontWeight: isActive ? 'bold' : 'normal',
                  cursor: 'pointer',
                  fontSize: '0.85rem'
                }}
                onClick={() => setRole(r.id)}
              >
                <Icon size={16} />
                <span>{r.label}</span>
              </button>
            );
          })}
        </div>

        {apiError && (
          <div className="auth-page__alert auth-page__alert--error" role="alert">
            {apiError}
          </div>
        )}

        <form className="auth-page__form" onSubmit={handleSubmit}>
          <div className="auth-page__form-row">
            <Input
              label="First Name"
              name="first_name"
              placeholder="Jane"
              value={form.first_name}
              onChange={handleChange}
              error={errors.first_name}
            />
            <Input
              label="Last Name"
              name="last_name"
              placeholder="Smith"
              value={form.last_name}
              onChange={handleChange}
              error={errors.last_name}
            />
          </div>
          <Input
            label="Username *"
            name="username"
            placeholder="janesmith"
            value={form.username}
            onChange={handleChange}
            error={errors.username}
            icon={User}
            required
          />
          <Input
            label="Email Address *"
            name="email"
            type="email"
            placeholder="jane@example.com"
            value={form.email}
            onChange={handleChange}
            error={errors.email}
            icon={Mail}
            required
          />
          <Input
            label="Phone Number"
            name="phone"
            type="tel"
            placeholder="+1 800 555 0199"
            value={form.phone}
            onChange={handleChange}
            error={errors.phone}
            icon={Phone}
          />

          {role === 'seller' && (
            <Input
              label="Store / Business Name *"
              name="business_name"
              placeholder="e.g. Apex Tech Store"
              value={form.business_name}
              onChange={handleChange}
              error={errors.business_name}
              icon={Building2}
            />
          )}

          <div className="auth-page__form-row">
            <Input
              label="Password *"
              name="password"
              type="password"
              placeholder="Min. 8 characters"
              value={form.password}
              onChange={handleChange}
              error={errors.password}
              icon={Lock}
              required
            />
            <Input
              label="Confirm Password *"
              name="password_confirm"
              type="password"
              placeholder="Re-enter password"
              value={form.password_confirm}
              onChange={handleChange}
              error={errors.password_confirm}
              icon={Lock}
              required
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            fullWidth
            size="lg"
            isLoading={isLoading}
          >
            Create {ROLES.find(r => r.id === role)?.label} Account
          </Button>
        </form>

        <div className="auth-page__footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="auth-page__link">Sign in to your account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
