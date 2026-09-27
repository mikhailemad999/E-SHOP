/**
 * CartPage — Shopping cart view with item quantity controls, price breakdown,
 * payment method selection (Cash on Delivery / VISA), and Order Receipt checkout.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, Trash2, ArrowRight, ShieldCheck, CreditCard, DollarSign, CheckCircle } from 'lucide-react';
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

  const subtotal = getTotalPrice();
  const shippingFee = subtotal > 0 ? 15.0 : 0.0;
  const tax = subtotal * 0.08;
  const grandTotal = subtotal + shippingFee + tax;

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
    };

    try {
      const { data } = await api.post('/checkout/', payload);
      const backendOrder = data.order || {};

      const formattedOrder = {
        id: backendOrder.id || Date.now(),
        tracking_number: backendOrder.order_number || `TRK-${Math.random().toString(36).substr(2, 8).toUpperCase()}`,
        created_at: new Date(backendOrder.created_at || Date.now()).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
        customer_name: user?.full_name || 'Valued Customer',
        customer_email: user?.email || 'customer@eshop.dev',
        customer_phone: user?.phone || '+1 800 555 0199',
        delivery_address: '101 Marketplace Blvd, New York, NY 10001',
        items: items.map((i) => ({ title: i.title, sku: i.sku || 'SKU-ITEM', quantity: i.quantity, price: i.price })),
        price: backendOrder.total_amount ? String(backendOrder.total_amount) : subtotal.toFixed(2),
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
        <h2>Order Placed Successfully!</h2>
        <p>Your order has been recorded in the database with Tracking Serial Number: <strong className="text-primary">{createdOrder.tracking_number}</strong></p>
        <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'center', gap: '16px' }}>
          <Button variant="primary" onClick={() => setCreatedOrder(createdOrder)}>
            View Official Order Receipt
          </Button>
          <Link to="/search">
            <Button variant="secondary">Continue Shopping</Button>
          </Link>
        </div>

        {createdOrder && (
          <ReceiptModal order={createdOrder} onClose={() => setCreatedOrder(null)} />
        )}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="container cart-empty animate-fade-in">
        <ShoppingCart size={64} className="cart-empty__icon" />
        <h2>Your Shopping Cart is Empty</h2>
        <p>Explore our catalog to add items to your cart.</p>
        <Link to="/search">
          <Button variant="primary" size="lg">Browse Catalog</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container cart-page animate-fade-in">
      <div className="cart-page__header">
        <h1>Shopping Cart ({items.reduce((sum, i) => sum + i.quantity, 0)} items)</h1>
      </div>

      <div className="cart-page__grid">
        {/* Left: Items List */}
        <div className="cart-items-list">
          {items.map((item) => (
            <div key={item.listing_id} className="cart-item-card">
              <img
                src={item.image}
                alt={item.title}
                className="cart-item__img"
                onError={(e) => handleImageError(e, '')}
              />
              <div className="cart-item__info">
                <h3>{item.title}</h3>
                <span className="cart-item__seller">Seller: {item.shop_name}</span>
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

          <div className="summary-row">
            <span>Subtotal</span>
            <span>${subtotal.toFixed(2)}</span>
          </div>
          <div className="summary-row">
            <span>Shipping Fee</span>
            <span>${shippingFee.toFixed(2)}</span>
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
