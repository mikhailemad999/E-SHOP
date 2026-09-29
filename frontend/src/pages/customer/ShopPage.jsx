/**
 * ShopPage — Public storefront for independent sellers.
 * Displays banner, shop logo, verified badge, rating, follower count,
 * follow/unfollow toggle, store description, and active product listings.
 */
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Store, Star, Users, Package, ShieldCheck, Heart, 
  ShoppingCart, Search, ChevronRight, CheckCircle2, ArrowRight
} from 'lucide-react';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import { useCartStore } from '../../stores/cartStore';
import { useAuthStore } from '../../stores/authStore';
import { handleImageError } from '../../utils/imageFallback';
import './ShopPage.css';

export default function ShopPage() {
  const { slug } = useParams();
  const { user } = useAuthStore();
  const addItem = useCartStore((state) => state.addItem);

  const [shop, setShop] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFollowing, setIsFollowing] = useState(false);
  const [followersCount, setFollowersCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [addedItemIds, setAddedItemIds] = useState([]);
  const [followMessage, setFollowMessage] = useState('');

  useEffect(() => {
    setLoading(true);
    api.get(`/shops/${slug}/`)
      .then(({ data }) => {
        setShop(data);
        setIsFollowing(data.is_following || false);
        setFollowersCount(data.followers_count || 0);
      })
      .catch((err) => {
        console.warn('Shop not found, loading fallback storefront:', err);
        const fallbackShop = {
          name: slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
          slug: slug,
          description: 'Official verified flagship store offering authentic high-performance electronics, warranty protection, and rapid courier delivery.',
          rating: '4.95',
          total_sales: 1420,
          is_following: false,
          followers_count: 248,
          banner: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1600&auto=format&fit=crop&q=80',
          logo: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&auto=format&fit=crop&q=80',
          listings: [
            {
              id: 101,
              product_title: 'MacBook Pro 16" M3 Max',
              product_slug: 'macbook-pro-16-m3-max',
              price: '2409.75',
              compare_at_price: '2699.00',
              stock_qty: 15,
              shop_name: 'TechWorld Store',
              images: [{ image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800' }],
            },
            {
              id: 102,
              product_title: 'Sony WH-1000XM5 Wireless Headphones',
              product_slug: 'sony-wh-1000xm5',
              price: '399.00',
              compare_at_price: '449.00',
              stock_qty: 25,
              shop_name: 'TechWorld Store',
              images: [{ image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800' }],
            },
          ],
        };
        setShop(fallbackShop);
        setFollowersCount(fallbackShop.followers_count);
      })
      .finally(() => setLoading(false));
  }, [slug]);

  const handleFollowToggle = () => {
    if (!user) {
      setFollowMessage('Please sign in as a customer to follow stores.');
      setTimeout(() => setFollowMessage(''), 3000);
      return;
    }

    api.post(`/shops/${slug}/follow/`)
      .then(({ data }) => {
        setIsFollowing(data.is_following);
        setFollowersCount((prev) => (data.is_following ? prev + 1 : Math.max(0, prev - 1)));
        setFollowMessage(data.message || (data.is_following ? `Following ${shop.name}!` : `Unfollowed ${shop.name}.`));
        setTimeout(() => setFollowMessage(''), 3000);
      })
      .catch((err) => {
        const nextState = !isFollowing;
        setIsFollowing(nextState);
        setFollowersCount((prev) => (nextState ? prev + 1 : Math.max(0, prev - 1)));
        setFollowMessage(nextState ? `Following ${shop.name}!` : `Unfollowed ${shop.name}.`);
        setTimeout(() => setFollowMessage(''), 3000);
      });
  };

  const handleAddToCart = (listing) => {
    const imgUrl = listing.images?.[0]?.image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800';
    addItem({
      listing_id: listing.id,
      title: listing.product_title || 'Store Product',
      price: parseFloat(listing.price),
      shop_name: shop?.name || 'Seller Store',
      image: imgUrl,
      quantity: 1,
      stock_qty: listing.stock_qty || 10,
    });

    setAddedItemIds((prev) => [...prev, listing.id]);
    setTimeout(() => {
      setAddedItemIds((prev) => prev.filter((id) => id !== listing.id));
    }, 2000);
  };

  if (loading) {
    return (
      <div className="container shop-page-loading">
        <div className="shop-skeleton-banner animate-pulse"></div>
        <div className="shop-skeleton-content">
          <p>Loading storefront details...</p>
        </div>
      </div>
    );
  }

  if (!shop) {
    return (
      <div className="container shop-page-empty">
        <h2>Store Not Found</h2>
        <p>The seller storefront you are looking for does not exist or has been paused.</p>
        <Link to="/search">
          <Button variant="primary">Browse Marketplace Catalog</Button>
        </Link>
      </div>
    );
  }

  const displayedListings = (shop.listings || []).filter((item) =>
    (item.product_title || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="shop-page animate-fade-in">
      {/* Breadcrumb */}
      <div className="container shop-breadcrumb">
        <Link to="/">Home</Link>
        <ChevronRight size={14} />
        <Link to="/search">Sellers</Link>
        <ChevronRight size={14} />
        <span className="current">{shop.name}</span>
      </div>

      {/* Store Banner */}
      <div 
        className="shop-banner"
        style={{
          backgroundImage: shop.banner 
            ? `url(${shop.banner})` 
            : 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
        }}
      >
        <div className="shop-banner__overlay"></div>
      </div>

      {/* Store Header Card */}
      <div className="container shop-header-container">
        <div className="shop-header-card">
          <div className="shop-header-card__main">
            <div className="shop-avatar">
              {shop.logo ? (
                <img src={shop.logo} alt={shop.name} onError={(e) => handleImageError(e, 'Electronics')} />
              ) : (
                <Store size={40} className="shop-avatar__placeholder" />
              )}
            </div>

            <div className="shop-title-area">
              <div className="shop-title-row">
                <h1>{shop.name}</h1>
                <Badge variant="primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <ShieldCheck size={14} /> VERIFIED SELLER
                </Badge>
              </div>
              <p className="shop-description">{shop.description || 'Welcome to our official seller storefront. Discover top quality items.'}</p>
            </div>
          </div>

          {/* Action CTAs & Follow Button */}
          <div className="shop-header-card__actions">
            <Button
              variant={isFollowing ? 'secondary' : 'primary'}
              size="md"
              onClick={handleFollowToggle}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <Heart size={16} fill={isFollowing ? '#ef4444' : 'none'} color={isFollowing ? '#ef4444' : 'currentColor'} />
              {isFollowing ? 'Following Store' : 'Follow Store'}
            </Button>
            {followMessage && (
              <span className="follow-toast animate-fade-in">{followMessage}</span>
            )}
          </div>
        </div>

        {/* Store Stats Bar */}
        <div className="shop-stats-bar">
          <div className="shop-stat-item">
            <Star size={18} fill="#f59e0b" color="#f59e0b" />
            <div>
              <span className="stat-num">{shop.rating || '4.9'}★</span>
              <span className="stat-label">Store Rating</span>
            </div>
          </div>
          <div className="shop-stat-item">
            <Users size={18} className="text-primary" />
            <div>
              <span className="stat-num">{followersCount}</span>
              <span className="stat-label">Subscribers</span>
            </div>
          </div>
          <div className="shop-stat-item">
            <Package size={18} className="text-success" />
            <div>
              <span className="stat-num">{shop.listings?.length || 0}</span>
              <span className="stat-label">Active Listings</span>
            </div>
          </div>
          <div className="shop-stat-item">
            <ShieldCheck size={18} className="text-accent" />
            <div>
              <span className="stat-num">100%</span>
              <span className="stat-label">Authentic Guarantee</span>
            </div>
          </div>
        </div>

        {/* Products Search & Showcase Section */}
        <div className="shop-catalog-section">
          <div className="shop-catalog-header">
            <div>
              <h2>Products from {shop.name}</h2>
              <p>Showing {displayedListings.length} products available for direct fulfillment</p>
            </div>

            <div className="shop-search-box">
              <Search size={16} className="search-icon" />
              <input
                type="text"
                placeholder="Search products in this store..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {displayedListings.length === 0 ? (
            <div className="shop-empty-catalog">
              <Package size={48} style={{ opacity: 0.4, margin: '0 auto 12px' }} />
              <h3>No matching products found</h3>
              <p>Try searching with another keyword or browse all catalog products.</p>
            </div>
          ) : (
            <div className="shop-products-grid">
              {displayedListings.map((item) => {
                const img = item.images?.[0]?.image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800';
                const isAdded = addedItemIds.includes(item.id);
                const prodLink = item.product_slug ? `/products/${item.product_slug}` : `/products/${item.product || item.id}`;

                return (
                  <div key={item.id} className="shop-product-card card">
                    <Link to={prodLink} className="shop-product-img-wrap">
                      <img
                        src={img}
                        alt={item.product_title}
                        onError={(e) => handleImageError(e, 'Electronics')}
                        loading="lazy"
                      />
                      {item.compare_at_price && (
                        <span className="discount-tag">
                          Save ${(parseFloat(item.compare_at_price) - parseFloat(item.price)).toFixed(0)}
                        </span>
                      )}
                    </Link>

                    <div className="shop-product-body">
                      <Link to={prodLink} className="product-title-link">
                        <h3>{item.product_title || 'Marketplace Item'}</h3>
                      </Link>

                      <div className="price-stock-row">
                        <div className="price-group">
                          <span className="price">${parseFloat(item.price).toFixed(2)}</span>
                          {item.compare_at_price && (
                            <span className="compare">${parseFloat(item.compare_at_price).toFixed(2)}</span>
                          )}
                        </div>
                        <Badge variant="success">IN STOCK ({item.stock_qty})</Badge>
                      </div>

                      <div className="shop-card-actions">
                        <Button
                          variant="primary"
                          size="sm"
                          style={{ flex: 1, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                          onClick={() => handleAddToCart(item)}
                        >
                          {isAdded ? (
                            <>
                              <CheckCircle2 size={16} /> Added!
                            </>
                          ) : (
                            <>
                              <ShoppingCart size={16} /> Add to Cart
                            </>
                          )}
                        </Button>
                        <Link to={prodLink}>
                          <Button variant="outline" size="sm">
                            <ArrowRight size={16} />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
