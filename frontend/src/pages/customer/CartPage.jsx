/**
 * CartPage — Shopping cart view with item quantity controls, promo codes,
 * seller storefront links, payment method selection (Cash on Delivery / VISA),
 * and Order Receipt checkout.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ShoppingCart, Trash2, ArrowRight, ShieldCheck, CreditCard, 
  DollarSign, CheckCircle, Tag, Check, AlertCircle 
} from 'lucide-react';
import api from '../../api/client';
import { useCartStore } from '../../stores/cartStore';
import { useAuthStore } from '../../stores/authStore';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import ReceiptModal from '../../components/molecules/ReceiptModal';
import { handleImageError } from '../../utils/imageFallback';
import './CartPage.css';

export default function CartPage() {
  const { items, removeItem, addItem, clearCart, getTotalPrice } = useCartStore();
  const { isAuthenticated, user } = useAuthStore();
  const navigate = useNavigate();

  const [paymentMethod, setPaymentMethod] = useState('VISA');
  const [createdOrder, setCreatedOrder] = useState(null);
  const [checkoutSuccess, setCheckoutSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [checkoutError, setCheckoutError] = useState('');

  // Promo code system
  const [promoCode, setPromoCode] = useState('');
  const [appliedPromo, setAppliedPromo] = useState(null);
  const [promoError, setPromoError] = useState('');

  const subtotal = getTotalPrice();
  let discountAmount = 0;
  let shippingFee = subtotal > 0 ? 15.0 : 0.0;

  if (appliedPromo) {
    if (appliedPromo.type === 'percentage') {
      discountAmount = (subtotal * appliedPromo.value) / 100;
    } else if (appliedPromo.type === 'shipping') {
      shippingFee = 0;
      discountAmount = 15.0;
    } else if (appliedPromo.type === 'fixed') {
      discountAmount = Math.min(subtotal, appliedPromo.value);
    }
  }

  const taxableAmount = Math.max(0, subtotal - (appliedPromo?.type === 'shipping' ? 0 : discountAmount));
  const tax = taxableAmount * 0.08;
  const grandTotal = Math.max(0, subtotal + (appliedPromo?.type === 'shipping' ? 0 : shippingFee) + tax - (appliedPromo?.type === 'shipping' ? 0 : discountAmount));

  const handleApplyPromo = (e) => {
    e.preventDefault();
    setPromoError('');
    const code = promoCode.trim().toUpperCase();

    if (code === 'WELCOME10') {
      setAppliedPromo({ code, type: 'percentage', value: 10, label: '10% New Buyer Discount' });
      setPromoCode('');
    } else if (code === 'SUPER20') {
      setAppliedPromo({ code, type: 'percentage', value: 20, label: '20% Summer Mega Sale' });
      setPromoCode('');
    } else if (code === 'FREESHIP') {
      setAppliedPromo({ code, type: 'shipping', value: 15, label: 'Free Express Shipping' });
      setPromoCode('');
    } else {
      setPromoError('Invalid coupon code. Try WELCOME10 or FREESHIP');
    }
  };

  const handleRemovePromo = () => {
    setAppliedPromo(null);
    setPromoError('');
  };

  const handleQuantityChange = (item, delta) => {
    if (item.quantity + delta <= 0) {
      removeItem(item.listing_id);
    } else {
      addItem({ ...item, quantity: delta });
    }
  };

  const handleCheckout = async () => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/cart');
      return;
    }

    setIsSubmitting(true);
    setCheckoutError('');

    const payload = {
      payment_method: paymentMethod === 'VISA' ? 'card' : 'cod',
      shipping_address: {
        full_name: user?.full_name || 'Valued Customer',
        phone: user?.phone || '+1 800 555 0199',
        address_line1: '101 Marketplace Blvd',
        city: 'New York',
        state: 'NY',
        postal_code: '10001',
        country: 'USA',
      },
      items: items.map((i) => ({
        listing_id: i.listing_id || i.id,
        quantity: i.quantity,
      })),
      notes: appliedPromo ? `Applied Promo: ${appliedPromo.code} (${appliedPromo.label})` : '',
    };

    try {
      const { data } = await api.post('/checkout/', payload);
      const backendOrder = data.order || {};

      const formattedOrder = {
        id: backendOrder.id || Date.now(),
        tracking_number: backendOrder.order_number || `ORD-${Math.random().toString(36).substr(2, 8).toUpperCase()}`,
        created_at: new Date(backendOrder.created_at || Date.now()).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
        customer_name: user?.full_name || 'Valued Customer',
        customer_email: user?.email || 'customer@eshop.dev',
        customer_phone: user?.phone || '+1 800 555 0199',
        delivery_address: '101 Marketplace Blvd, New York, NY 10001',
        items: items.map((i) => ({ title: i.title, sku: i.sku || 'SKU-ITEM', quantity: i.quantity, price: i.price })),
        price: backendOrder.total_amount ? String(backendOrder.total_amount) : grandTotal.toFixed(2),
        payment_method: paymentMethod,
        shop_name: items[0]?.shop_name || 'E-Shop Marketplace',
      };

      setCreatedOrder(formattedOrder);
      setCheckoutSuccess(true);
      clearCart();
    } catch (err) {
      console.error('Checkout error:', err);
      const errDetail = err.response?.data?.error || err.response?.data?.detail || 'Failed to process checkout. Please try again.';
      setCheckoutError(errDetail);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (checkoutSuccess && createdOrder) {
    return (
      <div className="container cart-page animate-fade-in" style={{ textAlign: 'center', padding: '60px 20px' }}>
        <CheckCircle size={64} className="text-success" style={{ margin: '0 auto 20px' }} />
        <h1>Order Confirmed & Placed!</h1>
        <p style={{ color: '#64748b', maxWidth: '500px', margin: '0 auto 24px' }}>
          Thank you for shopping with E-Shop. Your multi-vendor order <strong>#{createdOrder.tracking_number}</strong> has been transmitted to sellers and dispatch centers.
        </p>

        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <Button variant="primary" onClick={() => setCreatedOrder(createdOrder)}>
            View Order Receipt
          </Button>
          <Link to={`/track/${createdOrder.tracking_number}`}>
            <Button variant="outline">Live GPS Tracking</Button>
          </Link>
          <Link to="/">
            <Button variant="ghost">Continue Shopping</Button>
          </Link>
        </div>

        {createdOrder && (
          <ReceiptModal
            order={createdOrder}
            onClose={() => setCreatedOrder(null)}
          />
        )}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="container cart-page animate-fade-in">
        <div className="cart-empty-state">
          <ShoppingCart size={64} className="cart-empty-icon" />
          <h2>Your Cart is Empty</h2>
          <p>Discover high-performance electronics, fashion, and lifestyle items with verified seller guarantees.</p>
          <Link to="/search">
            <Button variant="primary" size="lg">Explore Products</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container cart-page animate-fade-in">
      <div className="cart-header">
        <h1>Shopping Cart ({items.reduce((sum, i) => sum + i.quantity, 0)} items)</h1>
        <button className="cart-clear-btn" onClick={clearCart}>Clear All</button>
      </div>

      <div className="cart-layout">
        {/* Left: Cart Items List */}
        <div className="cart-items-list">
          {items.map((item) => (
            <div key={item.listing_id} className="cart-item-card card">
              <img
                src={item.image || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800'}
                alt={item.title}
                className="cart-item__image"
                onError={(e) => handleImageError(e, 'Electronics')}
              />

              <div className="cart-item__details">
                <h3>{item.title}</h3>
                <span className="cart-item__seller">
                  Seller:{' '}
                  <Link
                    to={`/shop/${item.shop_slug || item.shop_name?.toLowerCase().replace(/\s+/g, '-') || 'techworld-premium'}`}
                    style={{ color: 'var(--color-primary, #2563eb)', textDecoration: 'none', fontWeight: 600 }}
                  >
                    {item.shop_name}
                  </Link>
                </span>
                <span className="cart-item__price">${item.price.toFixed(2)} each</span>
              </div>

              {/* Quantity Controls */}
              <div className="cart-item__qty-controls">
                <button onClick={() => handleQuantityChange(item, -1)}>-</button>
                <span>{item.quantity}</span>
                <button onClick={() => handleQuantityChange(item, 1)}>+</button>
              </div>

              <div className="cart-item__total">
                <span>${(item.price * item.quantity).toFixed(2)}</span>
              </div>

              <button className="cart-item__remove" onClick={() => removeItem(item.listing_id)} title="Remove Item">
                <Trash2 size={18} />
              </button>
            </div>
          ))}
        </div>

        {/* Right: Checkout Summary */}
        <div className="cart-summary-card">
          <h2>Order Summary</h2>

          {/* Payment Method Selector */}
          <div className="payment-method-selector">
            <label className="payment-label">Select Payment Method:</label>
            <div className="payment-options">
              <button
                type="button"
                className={`payment-btn ${paymentMethod === 'VISA' ? 'active' : ''}`}
                onClick={() => setPaymentMethod('VISA')}
              >
                <CreditCard size={18} />
                <span>VISA / Credit Card</span>
              </button>
              <button
                type="button"
                className={`payment-btn ${paymentMethod === 'CASH' ? 'active' : ''}`}
                onClick={() => setPaymentMethod('CASH')}
              >
                <DollarSign size={18} />
                <span>Cash on Delivery</span>
              </button>
            </div>
          </div>

          {/* Promo Code Form */}
          <form onSubmit={handleApplyPromo} style={{ margin: '16px 0', borderTop: '1px solid #e2e8f0', paddingTop: '16px' }}>
            <label style={{ fontSize: '0.825rem', fontWeight: 600, color: '#475569', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px' }}>
              <Tag size={14} /> Have a Promo Code?
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                placeholder="e.g. WELCOME10, FREESHIP"
                value={promoCode}
                onChange={(e) => setPromoCode(e.target.value)}
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: '1px solid #cbd5e1',
                  fontSize: '0.85rem',
                  textTransform: 'uppercase',
                }}
              />
              <Button type="submit" variant="secondary" size="sm">Apply</Button>
            </div>
            {promoError && (
              <span style={{ fontSize: '0.75rem', color: '#ef4444', display: 'block', marginTop: '4px' }}>
                {promoError}
              </span>
            )}
            {appliedPromo && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#ecfdf5', border: '1px solid #a7f3d0', padding: '6px 10px', borderRadius: '6px', marginTop: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: '#065f46', fontWeight: 600 }}>
                  <Check size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                  {appliedPromo.label} ({appliedPromo.code})
                </span>
                <button
                  type="button"
                  onClick={handleRemovePromo}
                  style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600 }}
                >
                  Remove
                </button>
              </div>
            )}
          </form>

          {/* Price Breakdown */}
          <div className="summary-row">
            <span>Subtotal</span>
            <span>${subtotal.toFixed(2)}</span>
          </div>

          {appliedPromo && discountAmount > 0 && (
            <div className="summary-row" style={{ color: '#16a34a', fontWeight: 600 }}>
              <span>Discount ({appliedPromo.code})</span>
              <span>-${discountAmount.toFixed(2)}</span>
            </div>
          )}

          <div className="summary-row">
            <span>Shipping Fee</span>
            <span>{appliedPromo?.type === 'shipping' ? <strong style={{ color: '#16a34a' }}>FREE</strong> : `$${shippingFee.toFixed(2)}`}</span>
          </div>
          <div className="summary-row">
            <span>Estimated Tax (8%)</span>
            <span>${tax.toFixed(2)}</span>
          </div>

          <div className="summary-row grand-total">
            <span>Total Amount</span>
            <span>${grandTotal.toFixed(2)}</span>
          </div>

          {checkoutError && (
            <div className="cart-checkout-error alert alert-danger" style={{ color: '#ef4444', marginBottom: '12px', fontSize: '0.9rem' }}>
              {checkoutError}
            </div>
          )}

          <Button variant="primary" size="lg" className="checkout-btn" onClick={handleCheckout} disabled={isSubmitting}>
            {isSubmitting ? 'Processing Order...' : 'Proceed to Checkout'}
            <ArrowRight size={18} style={{ marginLeft: '8px' }} />
          </Button>

          <div className="cart-trust-footer">
            <ShieldCheck size={16} /> 256-Bit SSL Encrypted & Buyer Protected
          </div>
        </div>
      </div>
    </div>
  );
}
