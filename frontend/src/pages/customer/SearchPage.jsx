/**
 * SearchPage — Product search grid with category tree sidebar filter, brand filters, and Buy-Box cards.
 */
import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Search, Filter, ShoppingBag, Layers } from 'lucide-react';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import { SkeletonCard } from '../../components/atoms/Skeleton';
import './SearchPage.css';

const CATEGORIES = [
  { name: 'All Products', slug: '' },
  { name: 'Electronics', slug: 'electronics' },
  { name: 'Smartphones & Tablets', slug: 'smartphones' },
  { name: 'Fashion & Apparel', slug: 'fashion' },
  { name: 'Luxury Watches', slug: 'watches' },
  { name: 'Home & Living', slug: 'home-living' },
  { name: 'Sports & Fitness', slug: 'sports' },
  { name: 'Beauty & Personal Care', slug: 'beauty' },
];

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';
  const categoryParam = searchParams.get('category') || '';

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState(queryParam);
  const [selectedCategory, setSelectedCategory] = useState(categoryParam);

  useEffect(() => {
    setLoading(true);
    let url = '/search/?';
    if (queryParam) url += `q=${encodeURIComponent(queryParam)}&`;
    if (categoryParam) url += `category__slug=${encodeURIComponent(categoryParam)}&`;

    api.get(url)
      .then(({ data }) => {
        setProducts(data.results || data);
      })
      .catch((err) => console.error('Search error:', err))
      .finally(() => setLoading(false));
  }, [queryParam, categoryParam]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setSearchParams({ q: searchTerm, category: selectedCategory });
  };

  const handleCategorySelect = (slug) => {
    setSelectedCategory(slug);
    const newParams = {};
    if (queryParam) newParams.q = queryParam;
    if (slug) newParams.category = slug;
    setSearchParams(newParams);
  };

  return (
    <div className="container search-page animate-fade-in">
      <div className="search-page__header">
        <h1>
          {queryParam ? `Search Results for "${queryParam}"` : categoryParam ? `Category: ${categoryParam.toUpperCase()}` : 'All Products Catalog'}
        </h1>
        <p>{products.length} products available</p>
      </div>

      <div className="search-page__layout">
        {/* Left Sidebar: Category Filter */}
        <aside className="search-page__sidebar">
          <div className="sidebar-box">
            <h3 className="sidebar-title">
              <Layers size={18} style={{ marginRight: '8px' }} />
              Product Categories
            </h3>
            <ul className="category-list">
              {CATEGORIES.map((cat) => (
                <li key={cat.slug}>
                  <button
                    className={`category-btn ${categoryParam === cat.slug ? 'active' : ''}`}
                    onClick={() => handleCategorySelect(cat.slug)}
                  >
                    {cat.name}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* Right Area: Products Grid */}
        <main className="search-page__results">
          {loading ? (
            <div className="product-grid">
              {Array.from({ length: 8 }).map((_, i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="search-page__empty">
              <ShoppingBag size={48} className="search-page__empty-icon" />
              <h3>No products found</h3>
              <p>Try searching with different keywords or selecting another category.</p>
            </div>
          ) : (
            <div className="product-grid">
              {products.map((prod) => (
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
                      {prod.category_name}
                    </Badge>
                  </div>
                  <div className="product-card__body">
                    <span className="product-card__brand">{prod.brand}</span>
                    <h3 className="product-card__title">{prod.title}</h3>
                    <div className="product-card__footer">
                      <div className="product-card__price">
                        <span className="product-card__price-label">From</span>
                        <span className="product-card__price-val">${prod.lowest_price}</span>
                      </div>
                      <Link to={`/products/${prod.slug}`}>
                        <Button variant="primary" size="sm">
                          View Details
                        </Button>
                      </Link>
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
