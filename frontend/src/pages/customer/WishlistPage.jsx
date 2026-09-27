/**
 * WishlistPage — Customer saved items with quick Add-to-Cart and removal.
 * Synchronized with MySQL backend API (/api/favorites/).
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Trash2, ShoppingCart, ArrowRight } from 'lucide-react';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import { useCartStore } from '../../stores/cartStore';
import './WishlistPage.css';

export default function WishlistPage() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const addItem = useCartStore((state) => state.addItem);

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = () => {
    setLoading(true);
    api.get('/favorites/')
      .then(({ data }) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setFavorites(list);
      })
      .catch((err) => {
        console.log('Using local favorites fallback:', err.message);
        setFavorites([]);
      })
      .finally(() => setLoading(false));
  };

  const handleRemove = (listingId) => {
    api.post(`/favorites/${listingId}/toggle/`)
      .then(() => {
        setFavorites(favorites.filter((fav) => fav.listing?.id !== listingId && fav.listing_id !== listingId));
      })
      .catch(() => {
        setFavorites(favorites.filter((fav) => fav.listing?.id !== listingId && fav.listing_id !== listingId));
      });
  };

  const handleAddToCart = (listing) => {
    if (!listing) return;
    addItem({
      listing_id: listing.id,
      title: listing.product?.title || listing.title || 'Product',
      price: parseFloat(listing.price),
      shop_name: listing.shop?.name || listing.shop_name || 'Verified Seller',
      image: listing.images?.[0]?.image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600',
      quantity: 1,
      stock_qty: listing.stock_qty || 10,
    });
  };

  return (
    <div className="container wishlist-page animate-fade-in">
      <div className="wishlist-header">
        <h1>My Wishlist & Saved Items</h1>
        <p>Keep track of products you love and want to purchase later.</p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 0', color: '#64748b' }}>
          Loading your saved wishlist...
        </div>
      ) : favorites.length === 0 ? (
        <div className="wishlist-empty">
          <Heart size={48} color="#94a3b8" style={{ margin: '0 auto' }} />
          <h3>Your wishlist is currently empty</h3>
          <p>Explore thousands of products across all categories and save your favorites.</p>
          <Link to="/search">
            <Button variant="primary">
              Discover Products <ArrowRight size={16} style={{ marginLeft: '6px' }} />
            </Button>
          </Link>
        </div>
      ) : (
        <div className="wishlist-grid">
          {favorites.map((fav) => {
            const listing = fav.listing || fav;
            const product = listing.product || {};
            const img = listing.images?.[0]?.image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600';
            const price = parseFloat(listing.price || 0).toFixed(2);
            const slug = product.slug || `product-${product.id || listing.id}`;

            return (
              <div key={fav.id || listing.id} className="wishlist-card">
                <div className="wishlist-card__image-wrap">
                  <img src={img} alt={product.title || 'Product'} className="wishlist-card__image" />
                  <button
                    className="wishlist-card__remove-btn"
                    onClick={() => handleRemove(listing.id)}
                    title="Remove from Wishlist"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                <div className="wishlist-card__content">
                  <span className="wishlist-card__shop">{listing.shop?.name || 'Verified Seller'}</span>
                  <Link to={`/products/${slug}`} className="wishlist-card__title">
                    {product.title || 'Marketplace Item'}
                  </Link>
                  <div className="wishlist-card__footer">
                    <span className="wishlist-card__price">${price}</span>
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => handleAddToCart(listing)}
                    >
                      <ShoppingCart size={14} style={{ marginRight: '6px' }} /> Add to Cart
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
