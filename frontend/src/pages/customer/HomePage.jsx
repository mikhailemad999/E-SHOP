/**
 * HomePage — Hero section, category grid, featured products, call-to-action.
 * Design: "Luxe Commercial" aesthetic per ui-ux-pro-max DFII ≥ 10 target.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight, Truck, ShieldCheck, CreditCard, Headphones,
  Smartphone, Laptop, Watch, Shirt, Home as HomeIcon,
  Dumbbell, Baby, Palette, Star,
} from 'lucide-react';
import Button from '../../components/atoms/Button';
import { SkeletonCard } from '../../components/atoms/Skeleton';
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
  { icon: Truck, title: 'Free Shipping', desc: 'On orders over $50' },
  { icon: ShieldCheck, title: 'Buyer Protection', desc: '30-day money back guarantee' },
  { icon: CreditCard, title: 'Secure Payments', desc: 'SSL encrypted checkout' },
  { icon: Headphones, title: '24/7 Support', desc: 'We\'re here to help' },
];

export default function HomePage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrending = async () => {
      try {
        const { data } = await axios.get(`${API_BASE_URL}/search/`);
        // API returns paginated results
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

  return (
    <div className="home">
      {/* ─── Hero Section ─────────────────────────────────── */}
      <section className="hero">
        <div className="container hero__inner">
          <div className="hero__content animate-fade-in-up">
            <span className="hero__badge">New Season Collection</span>
            <h1 className="hero__title">
              Discover Products
              <br />
              <span className="hero__title-accent">You'll Love</span>
            </h1>
            <p className="hero__subtitle">
              Shop from thousands of verified sellers. Best prices, fast delivery,
              and buyer protection on every order.
            </p>
            <div className="hero__actions">
              <Link to="/search">
                <Button variant="primary" size="lg" icon={ArrowRight} iconPosition="right">
                  Start Shopping
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
              <Laptop size={48} strokeWidth={1} />
              <span>Premium Tech</span>
            </div>
            <div className="hero__card hero__card--2">
              <div className="hero__card-shimmer" />
              <Watch size={48} strokeWidth={1} />
              <span>Luxury Watches</span>
            </div>
            <div className="hero__card hero__card--3">
              <div className="hero__card-shimmer" />
              <Shirt size={48} strokeWidth={1} />
              <span>Latest Fashion</span>
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
            <h2>Shop by Category</h2>
            <Link to="/search" className="home-section__link">
              View All <ArrowRight size={16} />
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
                  style={{ backgroundColor: `${cat.color}12`, color: cat.color }}
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
            <h2>Trending Now</h2>
            <Link to="/search?sort=trending" className="home-section__link">
              See All <ArrowRight size={16} />
            </Link>
          </div>
          <div className="product-grid">
            {loading ? (
              Array.from({ length: 4 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))
            ) : products.length > 0 ? (
              products.map((product) => (
                <Link
                  key={product.id || product.slug}
                  to={`/products/${product.slug}`}
                  className="product-card"
                >
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
                  <div className="product-card__body">
                    <h3 className="product-card__title">{product.title}</h3>
                    <p className="product-card__brand">{product.brand}</p>
                    <div className="product-card__footer">
                      <span className="product-card__price">
                        {product.lowest_price
                          ? `$${Number(product.lowest_price).toFixed(2)}`
                          : 'View Offers'}
                      </span>
                      {product.total_listings > 0 && (
                        <span className="product-card__sellers">
                          {product.total_listings} seller{product.total_listings > 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                </Link>
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
              Join our marketplace and reach millions of customers.
              Zero listing fees for your first 100 products.
            </p>
            <Link to="/register">
              <Button variant="primary" size="lg" icon={ArrowRight} iconPosition="right">
                Create Your Store
              </Button>
            </Link>
          </div>
          <div className="cta-banner__stats">
            <div className="cta-banner__stat">
              <span className="cta-banner__stat-value">10K+</span>
              <span className="cta-banner__stat-label">Products</span>
            </div>
            <div className="cta-banner__stat">
              <span className="cta-banner__stat-value">500+</span>
              <span className="cta-banner__stat-label">Sellers</span>
            </div>
            <div className="cta-banner__stat">
              <span className="cta-banner__stat-value">50K+</span>
              <span className="cta-banner__stat-label">Happy Customers</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

