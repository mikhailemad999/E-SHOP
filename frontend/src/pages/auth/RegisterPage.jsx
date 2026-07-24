/**
 * RegisterPage — Customer or Seller self-registration.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Phone, Building2 } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Input from '../../components/atoms/Input';
import './AuthPages.css';

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

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setApiError('');

    try {
      const endpoint = role === 'seller'
        ? '/auth/register/seller/'
        : '/auth/register/customer/';

      const { data } = await api.post(endpoint, form);
      login(data.user, data.tokens);
      navigate(role === 'seller' ? '/seller/dashboard' : '/');
    } catch (err) {
      const detail = err.response?.data;
      if (typeof detail === 'object' && detail !== null) {
        const fieldErrors = {};
        Object.entries(detail).forEach(([key, val]) => {
          fieldErrors[key] = Array.isArray(val) ? val[0] : val;
        });
        setErrors(fieldErrors);
      } else {
        setApiError('Registration failed. Please try again.');
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
          <h1 className="auth-page__title">Create your account</h1>
          <p className="auth-page__subtitle">Join thousands of buyers and sellers</p>
        </div>

        {/* Role Toggle */}
        <div className="auth-page__role-toggle">
          <button
            type="button"
            className={`auth-page__role-btn ${role === 'customer' ? 'auth-page__role-btn--active' : ''}`}
            onClick={() => setRole('customer')}
          >
            <User size={18} />
            I'm a Buyer
          </button>
          <button
            type="button"
            className={`auth-page__role-btn ${role === 'seller' ? 'auth-page__role-btn--active' : ''}`}
            onClick={() => setRole('seller')}
          >
            <Building2 size={18} />
            I'm a Seller
          </button>
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
              placeholder="John"
              value={form.first_name}
              onChange={handleChange}
              error={errors.first_name}
            />
            <Input
              label="Last Name"
              name="last_name"
              placeholder="Doe"
              value={form.last_name}
              onChange={handleChange}
              error={errors.last_name}
            />
          </div>
          <Input
            label="Username"
            name="username"
            placeholder="johndoe"
            value={form.username}
            onChange={handleChange}
            error={errors.username}
            icon={User}
            required
          />
          <Input
            label="Email"
            name="email"
            type="email"
            placeholder="john@example.com"
            value={form.email}
            onChange={handleChange}
            error={errors.email}
            icon={Mail}
            required
          />
          <Input
            label="Phone"
            name="phone"
            type="tel"
            placeholder="+1 234 567 8900"
            value={form.phone}
            onChange={handleChange}
            error={errors.phone}
            icon={Phone}
          />

          {role === 'seller' && (
            <Input
              label="Business Name"
              name="business_name"
              placeholder="Your store name"
              value={form.business_name}
              onChange={handleChange}
              error={errors.business_name}
              icon={Building2}
            />
          )}

          <div className="auth-page__form-row">
            <Input
              label="Password"
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
              label="Confirm Password"
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
            {role === 'seller' ? 'Create Seller Account' : 'Create Account'}
          </Button>
        </form>

        <div className="auth-page__footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="auth-page__link">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
