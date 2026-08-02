/**
 * HomePage — Hero section, category grid, featured products, call-to-action.
 * Design: "Luxe Commercial" aesthetic per ui-ux-pro-max guidelines.
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ArrowRight, Truck, ShieldCheck, CreditCard, Headphones,
  Smartphone, Laptop, Watch, Shirt, Home as HomeIcon,
  Dumbbell, Baby, Palette, Star, Search, Plus, Check, ShoppingCart
} from 'lucide-react';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import { SkeletonCard } from '../../components/atoms/Skeleton';
import { useCartStore } from '../../stores/cartStore';
import axios from 'axios';
import './HomePage.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const CATEGORIES = [
  { name: 'Electronics', icon: Laptop, color: '#6366f1', slug: 'electronics' },
  { name: 'Smartphones', icon: Smartphone, color: '#8b5cf6', slug: 'smartphones' },
  { name: 'Fashion', icon: Shirt, color: '#ec4899', slug: 'fashion' },
  { name: 'Watches', icon: Watch, color: '#f59e0b', slug: 'watches' },
  { name: 'Home & Living', icon: HomeIcon, color: '#10b981', slug: 'home-living' },
  { name: 'Sports', icon: Dumbbell, color: '#ef4444', slug: 'sports' },
  { name: 'Baby & Kids', icon: Baby, color: '#06b6d4', slug: 'baby-kids' },
  { name: 'Beauty', icon: Palette, color: '#f43f5e', slug: 'beauty' },
];

const FEATURES = [
  { icon: Truck, title: 'Free Global Shipping', desc: 'On all orders over $50' },
  { icon: ShieldCheck, title: 'Buyer Guarantee', desc: '30-day money back protection' },
  { icon: CreditCard, title: 'Encrypted Checkout', desc: '256-Bit SSL secured' },
  { icon: Headphones, title: '24/7 Expert Support', desc: 'Dedicated customer care' },
];

export default function HomePage() {
  const navigate = useNavigate();
  const addItemToCart = useCartStore((state) => state.addItem);

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [toastMessage, setToastMessage] = useState('');

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const { data } = await axios.get(`${API_BASE_URL}/search/`);
        const items = data.results || data || [];
        setProducts(items.slice(0, 8));
      } catch {
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchTrending();
  }, []);

  const handleHeroSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleAddToCart = (e, product) => {
    e.preventDefault();
    e.stopPropagation();

    addItemToCart({
      listing_id: product.id || Date.now(),
      title: product.title,
      price: parseFloat(product.lowest_price || product.price || 129.99),
      image: product.featured_image || product.image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800',
      shop_name: product.brand || 'Verified Seller',
      quantity: 1,
    });

    setToastMessage(`Added "${product.title}" to cart!`);
    setTimeout(() => setToastMessage(''), 3000);
  };

  return (
    <div className="home">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="home-toast animate-fade-in">
          <Check size={18} style={{ marginRight: '8px' }} />
          {toastMessage}
        </div>
      )}

      {/* ─── Hero Section ─────────────────────────────────── */}
      <section className="hero">
        <div className="container hero__inner">
          <div className="hero__content animate-fade-in-up">
            <span className="hero__badge">✨ Premier Multi-Vendor Marketplace</span>
            <h1 className="hero__title">
              Discover Products
              <br />
              <span className="hero__title-accent">You'll Love</span>
            </h1>
            <p className="hero__subtitle">
              Shop from verified international sellers with best prices, fast delivery,
              and 100% buyer protection guarantee.
            </p>

            {/* Interactive Hero Search Input */}
            <form className="hero__search-form" onSubmit={handleHeroSearch}>
              <Search size={20} className="hero__search-icon" />
              <input
                type="text"
                placeholder="What are you looking for today? (e.g. Sony WH-1000XM5)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="hero__search-input"
              />
              <Button type="submit" variant="primary" size="md">
                Search Catalog
              </Button>
            </form>

            <div className="hero__actions">
              <Link to="/search">
                <Button variant="primary" size="lg" icon={ArrowRight} iconPosition="right">
                  Browse All Deals
                </Button>
              </Link>
              <Link to="/register">
                <Button variant="secondary" size="lg">
                  Become a Seller
                </Button>
              </Link>
            </div>
          </div>

          <div className="hero__visual animate-fade-in">
            <div className="hero__card hero__card--1">
              <div className="hero__card-shimmer" />
              <Laptop size={44} strokeWidth={1.5} />
              <span>Premium Laptops</span>
              <Badge variant="success" size="sm">Hot Deal</Badge>
            </div>
            <div className="hero__card hero__card--2">
              <div className="hero__card-shimmer" />
              <Watch size={44} strokeWidth={1.5} />
              <span>Luxury Watches</span>
              <Badge variant="primary" size="sm">4.9 ★</Badge>
            </div>
            <div className="hero__card hero__card--3">
              <div className="hero__card-shimmer" />
              <Shirt size={44} strokeWidth={1.5} />
              <span>Designer Fashion</span>
              <Badge variant="warning" size="sm">Free Shipping</Badge>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Features Strip ───────────────────────────────── */}
      <section className="features-strip">
        <div className="container features-strip__inner">
          {FEATURES.map((f, i) => (
            <div key={i} className="features-strip__item">
              <f.icon size={24} className="features-strip__icon" />
              <div>
                <strong>{f.title}</strong>
                <span>{f.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ─── Categories ───────────────────────────────────── */}
      <section className="home-section">
        <div className="container">
          <div className="home-section__header">
            <div>
              <h2>Shop by Category</h2>
              <p className="home-section__sub">Curated selections from top global brands</p>
            </div>
            <Link to="/search" className="home-section__link">
              View All Categories <ArrowRight size={16} />
            </Link>
          </div>
          <div className="category-grid">
            {CATEGORIES.map((cat) => (
              <Link
                key={cat.slug}
                to={`/search?category=${cat.slug}`}
                className="category-card"
              >
                <div
                  className="category-card__icon"
                  style={{ backgroundColor: `${cat.color}14`, color: cat.color }}
                >
                  <cat.icon size={28} />
                </div>
                <span className="category-card__name">{cat.name}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Trending Products ──────────────────────────────── */}
      <section className="home-section home-section--alt">
        <div className="container">
          <div className="home-section__header">
            <div>
              <h2>Trending Offers</h2>
              <p className="home-section__sub">Handpicked bestsellers with live inventory auto-deduction</p>
            </div>
            <Link to="/search" className="home-section__link">
              See Full Catalog <ArrowRight size={16} />
            </Link>
          </div>
          <div className="product-grid">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))
            ) : products.length > 0 ? (
              products.map((product) => (
                <div
                  key={product.id || product.slug}
                  className="product-card"
                >
                  <div className="product-card__image-wrap">
                    {product.image ? (
                      <img
                        src={product.image}
                        alt={product.title}
                        className="product-card__img"
                        loading="lazy"
                      />
                    ) : (
                      <div className="product-card__img-placeholder">
                        <Laptop size={40} />
                      </div>
                    )}
                    <Badge variant="primary" className="product-card__badge">
                      {product.category_name || 'Trending'}
                    </Badge>
                  </div>
                  <div className="product-card__body">
                    <span className="product-card__brand">{product.brand || 'Verified Seller'}</span>
                    <h3 className="product-card__title">{product.title}</h3>
                    <div className="product-card__footer">
                      <div className="product-card__price">
                        <span className="product-card__price-label">Price</span>
                        <span className="product-card__price-val">
                          ${parseFloat(product.lowest_price || product.price || 99.99).toFixed(2)}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={(e) => handleAddToCart(e, product)}
                          title="Add to Cart"
                        >
                          <Plus size={16} />
                        </Button>
                        <Link to={`/products/${product.slug}`}>
                          <Button variant="primary" size="sm">
                            View
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="home-section__empty-note">
                Products will appear here once sellers add their listings.
              </p>
            )}
          </div>
        </div>
      </section>

      {/* ─── CTA Banner ───────────────────────────────────── */}
      <section className="cta-banner">
        <div className="container cta-banner__inner">
          <div className="cta-banner__content">
            <h2>Start Selling Today</h2>
            <p>
              Join our multi-vendor marketplace and reach thousands of active buyers worldwide.
              Zero listing fees for your first 100 products.
            </p>
            <Link to="/register">
              <Button variant="primary" size="lg" icon={ArrowRight} iconPosition="right">
                Create Seller Account
              </Button>
            </Link>
          </div>
          <div className="cta-banner__stats">
            <div className="cta-banner__stat">
              <span className="cta-banner__stat-value">10K+</span>
              <span className="cta-banner__stat-label">Live Listings</span>
            </div>
            <div className="cta-banner__stat">
              <span className="cta-banner__stat-value">500+</span>
              <span className="cta-banner__stat-label">Verified Stores</span>
            </div>
            <div className="cta-banner__stat">
              <span className="cta-banner__stat-value">99.8%</span>
              <span className="cta-banner__stat-label">Satisfied Buyers</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
