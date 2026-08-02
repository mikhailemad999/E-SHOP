/**
 * LoginPage — User authentication with 1-click Demo Account Fast Login for all roles.
 */
import { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { LogIn, Key, User, ShieldAlert, Sparkles } from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import Button from '../../components/atoms/Button';
import Input from '../../components/atoms/Input';
import './LoginPage.css';

const DEMO_ACCOUNTS = [
  { role: '👑 Super Admin', username: 'superadmin', pass: 'SuperAdmin123!', redirect: '/admin' },
  { role: '🛡️ System Admin', username: 'admin1', pass: 'AdminPass123!', redirect: '/admin' },
  { role: '🏪 Seller (TechWorld)', username: 'seller_techworld', pass: 'SellerPass123!', redirect: '/seller' },
  { role: '🚚 Delivery Manager', username: 'manager1', pass: 'ManagerPass123!', redirect: '/delivery' },
  { role: '🛵 Delivery Agent', username: 'agent1_1', pass: 'AgentPass123!', redirect: '/delivery/agent' },
  { role: '🛍️ Customer 1', username: 'customer1', pass: 'CustomerPass123!', redirect: '/' },
];

export default function LoginPage() {
  const [searchParams] = useSearchParams();
  const explicitRedirect = searchParams.get('redirect');

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, error } = useAuthStore();
  const navigate = useNavigate();

  const getRoleDefaultPath = (role) => {
    switch (role) {
      case 'SUPER_ADMIN':
      case 'ADMIN':
        return '/admin';
      case 'SELLER':
        return '/seller';
      case 'DELIVERY_MANAGER':
        return '/delivery';
      case 'DELIVERY_AGENT':
        return '/delivery/agent';
      default:
        return '/';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const success = await login(username, password);
    setLoading(false);

    if (success) {
      const loggedUser = useAuthStore.getState().user;
      const targetPath = explicitRedirect || getRoleDefaultPath(loggedUser?.role);
      navigate(targetPath);
    }
  };

  const handleFastLogin = async (account) => {
    setUsername(account.username);
    setPassword(account.pass);
    setLoading(true);
    const success = await login(account.username, account.pass);
    setLoading(false);
    if (success) {
      navigate(account.redirect);
    }
  };

  return (
    <div className="container login-page animate-fade-in">
      <div className="login-card">
        <div className="login-card__header">
          <h1>Welcome Back</h1>
          <p>Sign in to your E-Shop account</p>
        </div>

        {/* 1-Click Fast Login for Testing */}
        <div className="fast-login-box">
          <h3>
            <Sparkles size={16} className="text-primary" />
            1-Click Demo Account Selector
          </h3>
          <div className="fast-login-btns">
            {DEMO_ACCOUNTS.map((acc, i) => (
              <button
                key={i}
                type="button"
                className="fast-login-btn"
                onClick={() => handleFastLogin(acc)}
              >
                Log in as <strong>{acc.role}</strong>
              </button>
            ))}
          </div>
        </div>

        {error && <div className="login-card__error">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <Input
            label="Username or Email"
            type="text"
            placeholder="seller1 or seller1@eshop.dev"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <Button type="submit" variant="primary" fullWidth disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In'}
          </Button>
        </form>

        <div className="login-card__footer">
          <p>Don't have an account? <Link to="/register">Create Account</Link></p>
        </div>
      </div>
    </div>
  );
}
