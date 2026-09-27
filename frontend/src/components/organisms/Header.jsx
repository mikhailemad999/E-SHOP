/**
 * Header organism — navigation with search, cart badge count, notifications center, wishlist, and auth.
 */
import { Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, User, LogOut, Menu, X, Heart, Bell, CheckCircle } from 'lucide-react';
import { useEffect, useState, useRef } from 'react';
import api from '../../api/client';
import { useAuthStore } from '../../stores/authStore';
import { useCartStore } from '../../stores/cartStore';
import Button from '../atoms/Button';
import './Header.css';

export default function Header() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const cartItemCount = useCartStore((state) => state.getItemCount());

  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Notifications state
  const [notifsOpen, setNotifsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const notifRef = useRef(null);

  useEffect(() => {
    if (isAuthenticated) {
      loadNotifications();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setNotifsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadNotifications = () => {
    api.get('/notifications/')
      .then(({ data }) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setNotifications(list);
        setUnreadCount(list.filter((n) => !n.is_read).length);
      })
      .catch(() => {
        // Fallback demo notifications
        setNotifications([
          {
            id: 1,
            title: 'Welcome to E-Shop',
            message: 'Discover products from top sellers across electronics, fashion, and home.',
            is_read: false,
            created_at: new Date().toISOString(),
          },
        ]);
        setUnreadCount(1);
      });
  };

  const handleMarkAllRead = () => {
    api.post('/notifications/read-all/')
      .then(() => {
        setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
        setUnreadCount(0);
      })
      .catch(() => {
        setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
        setUnreadCount(0);
      });
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <header className="header">
      <div className="container header__inner">
        {/* Logo */}
        <Link to="/" className="header__logo">
          <span className="header__logo-icon">◆</span>
          <span className="header__logo-text">E-Shop</span>
        </Link>

        {/* Search Bar */}
        <form className="header__search" onSubmit={handleSearch}>
          <Search size={18} className="header__search-icon" />
          <input
            type="search"
            placeholder="Search products, brands, and categories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="header__search-input"
          />
        </form>

        {/* Customer Navigation Links */}
        <div className="header__nav-links">
          <Link to="/search" className="header__nav-link">Explore Catalog</Link>
          <Link to="/wishlist" className="header__nav-link">Wishlist</Link>
        </div>

        {/* Actions */}
        <nav className="header__actions">
          {/* Wishlist Link */}
          <Link to="/wishlist" className="header__action-btn" aria-label="Wishlist" title="My Wishlist">
            <Heart size={20} />
          </Link>

          {/* Shopping Cart with Badge */}
          <Link to="/cart" className="header__action-btn header__cart-btn" aria-label="Cart">
            <ShoppingCart size={20} />
            {cartItemCount > 0 && (
              <span className="header__cart-badge">{cartItemCount}</span>
            )}
          </Link>

          {/* In-App Notifications Center */}
          {isAuthenticated && (
            <div className="header__notif-container" ref={notifRef}>
              <button
                className="header__action-btn header__cart-btn"
                onClick={() => setNotifsOpen(!notifsOpen)}
                aria-label="Notifications"
                title="Notifications"
              >
                <Bell size={20} />
                {unreadCount > 0 && (
                  <span className="header__cart-badge" style={{ background: '#3b82f6' }}>{unreadCount}</span>
                )}
              </button>

              {notifsOpen && (
                <div className="header__notif-dropdown animate-fade-in">
                  <div className="header__notif-header">
                    <h4>Notifications</h4>
                    {unreadCount > 0 && (
                      <button className="header__notif-mark-all" onClick={handleMarkAllRead}>
                        Mark all as read
                      </button>
                    )}
                  </div>
                  <div className="header__notif-list">
                    {notifications.length === 0 ? (
                      <div className="header__notif-empty">No notifications yet.</div>
                    ) : (
                      notifications.map((notif) => (
                        <div
                          key={notif.id}
                          className={`header__notif-item ${!notif.is_read ? 'unread' : ''}`}
                        >
                          <div className="header__notif-title">{notif.title}</div>
                          <div className="header__notif-message">{notif.message}</div>
                          <div className="header__notif-time">
                            {notif.created_at ? new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Now'}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          <Link to="/profile" className="header__action-btn" aria-label="Profile" title="Profile">
            <User size={20} />
          </Link>

          {isAuthenticated ? (
            <button className="header__action-btn" onClick={handleLogout} aria-label="Logout" title={`Logged in as ${user?.username || 'User'}`}>
              <LogOut size={20} />
            </button>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="sm">Log In</Button>
              </Link>
              <Link to="/register">
                <Button variant="primary" size="sm">Sign Up</Button>
              </Link>
            </>
          )}
          <button
            className="header__mobile-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </nav>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="header__mobile-menu animate-fade-in">
          <form className="header__mobile-search" onSubmit={handleSearch}>
            <Search size={18} />
            <input
              type="search"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </form>
          <div className="header__mobile-links">
            <Link to="/search" onClick={() => setMobileMenuOpen(false)}>Explore Catalog</Link>
            <Link to="/wishlist" onClick={() => setMobileMenuOpen(false)}>My Wishlist</Link>
            <Link to="/cart" onClick={() => setMobileMenuOpen(false)}>Shopping Cart ({cartItemCount})</Link>
            <Link to="/profile" onClick={() => setMobileMenuOpen(false)}>My Profile</Link>
          </div>
        </div>
      )}
    </header>
  );
}
