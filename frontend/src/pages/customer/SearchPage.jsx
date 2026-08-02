/**
 * SearchPage — Comprehensive product search & multi-facet filtering catalog.
 * Supports keyword search, category selection, price range filters, sorting,
 * and direct Add-to-Cart integration.
 */
import { useEffect, useState, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, Filter, ShoppingBag, Layers, DollarSign, SlidersHorizontal, ArrowUpDown, Check, Plus } from 'lucide-react';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import { SkeletonCard } from '../../components/atoms/Skeleton';
import { useCartStore } from '../../stores/cartStore';
import './SearchPage.css';

const CATEGORIES = [
  { name: 'All Categories', slug: '' },
  { name: 'Electronics', slug: 'electronics' },
  { name: 'Smartphones & Tablets', slug: 'smartphones' },
  { name: 'Fashion & Apparel', slug: 'fashion' },
  { name: 'Luxury Watches', slug: 'watches' },
  { name: 'Home & Living', slug: 'home-living' },
  { name: 'Sports & Fitness', slug: 'sports' },
  { name: 'Beauty & Personal Care', slug: 'beauty' },
];

const PRICE_PRESETS = [
  { label: 'All Prices', min: '', max: '' },
  { label: 'Under $100', min: '0', max: '100' },
  { label: '$100 - $500', min: '100', max: '500' },
  { label: '$500 - $1,000', min: '500', max: '1000' },
  { label: '$1,000+', min: '1000', max: '' },
];

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';
  const categoryParam = searchParams.get('category') || '';

  const addItemToCart = useCartStore((state) => state.addItem);

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filter States
  const [searchTerm, setSearchTerm] = useState(queryParam);
  const [selectedCategory, setSelectedCategory] = useState(categoryParam);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [sortBy, setSortBy] = useState('default');
  const [toastMessage, setToastMessage] = useState('');

  // Sync URL search params with state
  useEffect(() => {
    setSearchTerm(queryParam);
    setSelectedCategory(categoryParam);
  }, [queryParam, categoryParam]);

  // Fetch catalog from API
  useEffect(() => {
    setLoading(true);
    let url = '/search/?';
    if (queryParam) url += `q=${encodeURIComponent(queryParam)}&`;
    if (categoryParam) url += `category__slug=${encodeURIComponent(categoryParam)}&`;

    api.get(url)
      .then(({ data }) => {
        setProducts(data.results || data || []);
      })
      .catch((err) => console.error('Search API error:', err))
      .finally(() => setLoading(false));
  }, [queryParam, categoryParam]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    const newParams = {};
    if (searchTerm.trim()) newParams.q = searchTerm.trim();
    if (selectedCategory) newParams.category = selectedCategory;
    setSearchParams(newParams);
  };

  const handleCategorySelect = (slug) => {
    setSelectedCategory(slug);
    const newParams = {};
    if (searchTerm.trim()) newParams.q = searchTerm.trim();
    if (slug) newParams.category = slug;
    setSearchParams(newParams);
  };

  const handlePresetPrice = (preset) => {
    setMinPrice(preset.min);
    setMaxPrice(preset.max);
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedCategory('');
    setMinPrice('');
    setMaxPrice('');
    setSortBy('default');
    setSearchParams({});
  };

  const handleAddToCart = (e, prod) => {
    e.preventDefault();
    e.stopPropagation();

    addItemToCart({
      listing_id: prod.id || Date.now(),
      title: prod.title,
      price: parseFloat(prod.lowest_price || prod.price || 99.99),
      image: prod.featured_image || prod.image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800',
      shop_name: prod.shop_name || 'E-Shop Marketplace',
      quantity: 1,
    });

    setToastMessage(`Added "${prod.title}" to your cart!`);
    setTimeout(() => setToastMessage(''), 3000);
  };

  // Client-side filtering & sorting engine
  const filteredProducts = useMemo(() => {
    return products.filter((prod) => {
      const price = parseFloat(prod.lowest_price || prod.price || 0);

      // Search term filter
      if (searchTerm && !prod.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
          !(prod.brand && prod.brand.toLowerCase().includes(searchTerm.toLowerCase()))) {
        return false;
      }

      // Min price filter
      if (minPrice !== '' && price < parseFloat(minPrice)) {
        return false;
      }

      // Max price filter
      if (maxPrice !== '' && price > parseFloat(maxPrice)) {
        return false;
      }

      return true;
    }).sort((a, b) => {
      const priceA = parseFloat(a.lowest_price || a.price || 0);
      const priceB = parseFloat(b.lowest_price || b.price || 0);

      if (sortBy === 'price_asc') return priceA - priceB;
      if (sortBy === 'price_desc') return priceB - priceA;
      if (sortBy === 'title_asc') return a.title.localeCompare(b.title);
      return 0;
    });
  }, [products, searchTerm, minPrice, maxPrice, sortBy]);

  return (
    <div className="container search-page animate-fade-in">
      {/* Top Banner & Header */}
      <div className="search-page__header">
        <div>
          <h1>
            {queryParam ? `Search Results for "${queryParam}"` : selectedCategory ? `Category: ${selectedCategory.toUpperCase()}` : 'Product Catalog & Search'}
          </h1>
          <p>Showing {filteredProducts.length} filtered offer{filteredProducts.length !== 1 ? 's' : ''} from verified sellers</p>
        </div>

        {/* Global Search Bar in Header */}
        <form className="search-bar-inline" onSubmit={handleSearchSubmit}>
          <Search size={18} className="search-bar-inline__icon" />
          <input
            type="text"
            placeholder="Search keywords, brands, models..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-bar-inline__input"
          />
          <Button type="submit" variant="primary" size="sm">Search</Button>
        </form>
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="search-toast animate-fade-in">
          <Check size={18} style={{ marginRight: '8px' }} />
          {toastMessage}
        </div>
      )}

      <div className="search-page__layout">
        {/* Left Sidebar Filters */}
        <aside className="search-page__sidebar">
          {/* Categories Box */}
          <div className="sidebar-box">
            <h3 className="sidebar-title">
              <Layers size={18} style={{ marginRight: '8px' }} />
              Product Categories
            </h3>
            <ul className="category-list">
              {CATEGORIES.map((cat) => (
                <li key={cat.slug}>
                  <button
                    className={`category-btn ${selectedCategory === cat.slug ? 'active' : ''}`}
                    onClick={() => handleCategorySelect(cat.slug)}
                  >
                    {cat.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Price Range Filter Box */}
          <div className="sidebar-box">
            <h3 className="sidebar-title">
              <DollarSign size={18} style={{ marginRight: '4px' }} />
              Price Filter ($)
            </h3>
            <div className="price-inputs">
              <input
                type="number"
                placeholder="Min $"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                className="price-input"
              />
              <span>to</span>
              <input
                type="number"
                placeholder="Max $"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                className="price-input"
              />
            </div>
            <div className="price-presets">
              {PRICE_PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`price-preset-chip ${minPrice === p.min && maxPrice === p.max ? 'active' : ''}`}
                  onClick={() => handlePresetPrice(p)}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Reset Filters */}
          <Button variant="secondary" size="md" className="reset-filters-btn" onClick={handleResetFilters}>
            <SlidersHorizontal size={16} style={{ marginRight: '6px' }} />
            Reset All Filters
          </Button>
        </aside>

        {/* Right Area: Sort & Product Grid */}
        <main className="search-page__results">
          {/* Sorting Bar */}
          <div className="search-sort-bar">
            <span className="search-sort-bar__count">
              Found <strong>{filteredProducts.length}</strong> product{filteredProducts.length !== 1 ? 's' : ''}
            </span>

            <div className="search-sort-bar__controls">
              <ArrowUpDown size={16} style={{ marginRight: '6px' }} />
              <label htmlFor="sortSelect" className="sort-label">Sort by:</label>
              <select
                id="sortSelect"
                className="sort-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="default">Relevance / Featured</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="title_asc">Name: A to Z</option>
              </select>
            </div>
          </div>

          {/* Product Cards Grid */}
          {loading ? (
            <div className="product-grid">
              {Array.from({ length: 8 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : filteredProducts.length === 0 ? (
            <div className="search-page__empty">
              <ShoppingBag size={48} className="search-page__empty-icon" />
              <h3>No matching products found</h3>
              <p>Try adjusting your search query, price sliders, or category selection.</p>
              <Button variant="primary" size="md" onClick={handleResetFilters} style={{ marginTop: '16px' }}>
                Clear Filters
              </Button>
            </div>
          ) : (
            <div className="product-grid">
              {filteredProducts.map((prod) => (
                <div key={prod.id} className="product-card">
                  <div className="product-card__image-wrap">
                    {prod.featured_image ? (
                      <img src={prod.featured_image} alt={prod.title} className="product-card__image" />
                    ) : (
                      <div className="product-card__placeholder">
                        <ShoppingBag size={32} />
                      </div>
                    )}
                    <Badge variant="primary" className="product-card__badge">
                      {prod.category_name || 'Featured'}
                    </Badge>
                  </div>
                  <div className="product-card__body">
                    <span className="product-card__brand">{prod.brand || 'Original'}</span>
                    <h3 className="product-card__title">{prod.title}</h3>
                    <div className="product-card__footer">
                      <div className="product-card__price">
                        <span className="product-card__price-label">Price</span>
                        <span className="product-card__price-val">${parseFloat(prod.lowest_price || prod.price || 99.99).toFixed(2)}</span>
                      </div>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={(e) => handleAddToCart(e, prod)}
                          title="Add to Cart"
                        >
                          <Plus size={16} />
                        </Button>
                        <Link to={`/products/${prod.slug}`}>
                          <Button variant="primary" size="sm">
                            Details
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
