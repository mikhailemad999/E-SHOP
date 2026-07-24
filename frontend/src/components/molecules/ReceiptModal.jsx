/**
 * ReceiptModal — Formal printable Order Receipt / Tax Invoice.
 * Displays Serial Tracking Number, Customer Info, Items, Prices, Taxes, and Payment Method.
 */
import { Printer, X, CheckCircle, CreditCard, DollarSign } from 'lucide-react';
import Button from '../atoms/Button';
import Badge from '../atoms/Badge';
import './ReceiptModal.css';

export default function ReceiptModal({ order, onClose }) {
  if (!order) return null;

  const handlePrint = () => {
    window.print();
  };

  const paymentLabel = order.payment_method === 'CASH' ? 'Cash on Delivery (COD)' : 'VISA / Credit Card (Prepaid)';

  return (
    <div className="modal-backdrop">
      <div className="receipt-modal animate-fade-in">
        <div className="receipt-header no-print">
          <h2>Official Sales Receipt / Tax Invoice</h2>
          <div className="receipt-header-actions">
            <Button variant="secondary" size="sm" onClick={handlePrint}>
              <Printer size={16} style={{ marginRight: '6px' }} />
              Print Receipt
            </Button>
            <button className="modal-close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Printable Receipt Body */}
        <div className="receipt-paper">
          <div className="receipt-paper__brand">
            <h1>E-Shop Marketplace</h1>
            <p>Official Purchase Receipt & Tax Invoice</p>
          </div>

          <div className="receipt-paper__meta">
            <div>
              <span className="meta-label">Serial / Tracking No:</span>
              <strong className="meta-value text-primary">{order.tracking_number || 'TRK-98A7F6B120'}</strong>
            </div>
            <div>
              <span className="meta-label">Order Date:</span>
              <span className="meta-value">{order.created_at || 'July 24, 2026'}</span>
            </div>
            <div>
              <span className="meta-label">Payment Status:</span>
              <Badge variant="success">PAID / VERIFIED</Badge>
            </div>
          </div>

          <div className="receipt-paper__grid">
            {/* Customer Information */}
            <div className="receipt-box">
              <h3>Customer Information</h3>
              <p><strong>Name:</strong> {order.customer_name || 'Customer 1 Test'}</p>
              <p><strong>Email:</strong> {order.customer_email || 'customer1@eshop.dev'}</p>
              <p><strong>Phone:</strong> {order.customer_phone || '+1 800 555 0001'}</p>
              <p><strong>Delivery Address:</strong> {order.delivery_address || '101 Marketplace Blvd, New York, NY 10001'}</p>
            </div>

            {/* Payment Method Details */}
            <div className="receipt-box">
              <h3>Payment & Billing</h3>
              <p><strong>Payment Method:</strong> {paymentLabel}</p>
              <p><strong>Transaction ID:</strong> TXN-{Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
              <p><strong>Store Name:</strong> {order.shop_name || 'TechWorld Premium'}</p>
            </div>
          </div>

          {/* Purchased Items Table */}
          <div className="receipt-table-wrap">
            <table className="receipt-table">
              <thead>
                <tr>
                  <th>Product Description</th>
                  <th>SKU</th>
                  <th>Qty</th>
                  <th>Unit Price</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {(order.items || [
                  { title: order.product_title || 'MacBook Pro 16" M3 Max', sku: 'SKU-APP-001', quantity: order.quantity || 1, price: order.price || '2409.75' }
                ]).map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.title}</td>
                    <td><code>{item.sku || 'SKU-001'}</code></td>
                    <td>{item.quantity}</td>
                    <td>${item.price}</td>
                    <td>${(parseFloat(item.price) * item.quantity).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Money Totals */}
          <div className="receipt-totals">
            <div className="totals-row">
              <span>Subtotal:</span>
              <span>${order.subtotal || order.price || '2409.75'}</span>
            </div>
            <div className="totals-row">
              <span>Shipping Fee:</span>
              <span>$15.00</span>
            </div>
            <div className="totals-row">
              <span>Tax (8%):</span>
              <span>${((parseFloat(order.price || 2409.75) * 0.08)).toFixed(2)}</span>
            </div>
            <div className="totals-row grand-total">
              <span>Grand Total:</span>
              <span>${(parseFloat(order.price || 2409.75) * 1.08 + 15).toFixed(2)}</span>
            </div>
          </div>

          <div className="receipt-footer">
            <p>Thank you for shopping on E-Shop Multi-Vendor Marketplace!</p>
            <p className="small">For support or returns, visit http://localhost:5173/track/{order.tracking_number || 'TRK-98A7F6B120'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
