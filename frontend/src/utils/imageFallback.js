/**
 * Smart Image Fallbacks for E-Shop Marketplace
 * Provides high-resolution, reliable category-specific fallback images
 * whenever a product image is missing or fails to load.
 */

const CATEGORY_FALLBACKS = {
  electronics: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800',
  smartphones: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800',
  'smartphones & tablets': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800',
  fashion: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800',
  'fashion & apparel': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800',
  watches: 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800',
  'luxury watches': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800',
  'home & living': 'https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=800',
  'sports & fitness': 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800',
  sports: 'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800',
  beauty: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800',
  'beauty & personal care': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800',
};

const DEFAULT_FALLBACK = 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800';

export function getProductImage(product) {
  if (!product) return DEFAULT_FALLBACK;
  if (product.featured_image) return product.featured_image;
  if (product.image) return product.image;
  if (product.images && product.images.length > 0) {
    const first = product.images[0];
    return typeof first === 'string' ? first : first.image || DEFAULT_FALLBACK;
  }
  const cat = (product.category_name || product.category?.name || '').toLowerCase();
  return CATEGORY_FALLBACKS[cat] || DEFAULT_FALLBACK;
}

export function handleImageError(e, categoryName) {
  const cat = (categoryName || '').toLowerCase();
  const fallback = CATEGORY_FALLBACKS[cat] || DEFAULT_FALLBACK;
  if (e.currentTarget.src !== fallback) {
    e.currentTarget.src = fallback;
  }
}
