/**
 * Header organism — navigation with search, cart badge count, auth, and role-aware quick links.
 */
import { Link, useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, User, LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';
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
        </div>

        {/* Actions */}
        <nav className="header__actions">
          {/* Shopping Cart with Badge */}
          <Link to="/cart" className="header__action-btn header__cart-btn" aria-label="Cart">
            <ShoppingCart size={20} />
            {cartItemCount > 0 && (
              <span className="header__cart-badge">{cartItemCount}</span>
            )}
          </Link>

          <Link to="/profile" className="header__action-btn" aria-label="Profile">
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
            <Link to="/cart" onClick={() => setMobileMenuOpen(false)}>Shopping Cart ({cartItemCount})</Link>
            <Link to="/profile" onClick={() => setMobileMenuOpen(false)}>My Profile</Link>
          </div>
        </div>
      )}
    </header>
  );
}
