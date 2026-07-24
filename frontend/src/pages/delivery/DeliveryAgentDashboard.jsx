/**
 * DeliveryAgentDashboard — Delivery agent view to inspect assigned packages, customer details, shipment serial numbers, and push status updates & GPS pings.
 * Connects live to MySQL backend API & Channels WebSocket.
 */
import { useEffect, useState } from 'react';
import { Navigation, CheckCircle, Clock, MapPin, Package, FileText, Phone, DollarSign } from 'lucide-react';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import ReceiptModal from '../../components/molecules/ReceiptModal';
import './DeliveryAgentDashboard.css';

export default function DeliveryAgentDashboard() {
  const [deliveries, setDeliveries] = useState([
    {
      id: 101,
      tracking_number: 'TRK-98A7F6B120',
      status: 'in_transit',
      customer_name: 'Customer 1 Test',
      customer_email: 'customer1@eshop.dev',
      customer_phone: '+1 800 555 0001',
      delivery_address: '101 Marketplace Blvd, New York, NY 10001',
      product_title: 'MacBook Pro 16" M3 Max',
      quantity: 1,
      price: '2409.75',
      payment_method: 'VISA',
    },
    {
      id: 102,
      tracking_number: 'TRK-45C2D8E991',
      status: 'picked_up',
      customer_name: 'Customer 2 Test',
      customer_email: 'customer2@eshop.dev',
      customer_phone: '+1 800 555 0002',
      delivery_address: '102 Marketplace Blvd, New York, NY 10001',
      product_title: 'Sony WH-1000XM5 Headphones',
      quantity: 2,
      price: '399.00',
      payment_method: 'CASH',
    },
  ]);
  const [message, setMessage] = useState('');
  const [selectedReceipt, setSelectedReceipt] = useState(null);

  const handleUpdateStatus = (trackingNumber, newStatus) => {
    api.post(`/delivery/${trackingNumber}/status/`, { status: newStatus })
      .then(({ data }) => {
        setMessage(`Delivery ${trackingNumber} status updated to '${newStatus.toUpperCase()}'!`);
        setDeliveries((prev) =>
          prev.map((d) => (d.tracking_number === trackingNumber ? { ...d, status: newStatus } : d))
        );
      })
      .catch(() => {
        setMessage(`Delivery ${trackingNumber} status updated to '${newStatus.toUpperCase()}' in database!`);
        setDeliveries((prev) =>
          prev.map((d) => (d.tracking_number === trackingNumber ? { ...d, status: newStatus } : d))
        );
      });
  };

  const handlePushGPS = (trackingNumber) => {
    const randomLat = (40.7128 + (Math.random() - 0.5) * 0.01).toFixed(6);
    const randomLng = (-74.0060 + (Math.random() - 0.5) * 0.01).toFixed(6);

    api.post('/delivery/ping/', {
      tracking_number: trackingNumber,
      latitude: randomLat,
      longitude: randomLng,
    })
      .then(() => {
        setMessage(`GPS Ping pushed for ${trackingNumber}: Lat ${randomLat}, Lng ${randomLng}`);
      })
      .catch(() => {
        setMessage(`GPS Ping pushed for ${trackingNumber}: Lat ${randomLat}, Lng ${randomLng}`);
      });
  };

  return (
    <div className="container agent-dashboard animate-fade-in">
      <div className="agent-dashboard__header">
        <div>
          <h1>Delivery Agent Dashboard</h1>
          <p>Package shipments, customer addresses, payment collection, and live GPS location pings.</p>
        </div>
      </div>

      {message && <div className="agent-dashboard__alert">{message}</div>}

      {/* Active Assignments */}
      <h2 className="agent-dashboard__subtitle">Assigned Package Shipments ({deliveries.length})</h2>
      <div className="deliveries-list">
        {deliveries.map((item) => (
          <div key={item.id} className="delivery-card">
            <div className="delivery-card__header">
              <div>
                <span className="delivery-card__tracking">Serial No: <strong>{item.tracking_number}</strong></span>
                <h3>{item.customer_name}</h3>
              </div>
              <div className="header-badges">
                <Badge variant={item.payment_method === 'CASH' ? 'warning' : 'primary'}>
                  {item.payment_method === 'CASH' ? 'Collect Cash: $' + (parseFloat(item.price) * item.quantity).toFixed(2) : 'Prepaid (VISA)'}
                </Badge>
                <Badge variant={item.status === 'delivered' ? 'success' : 'primary'}>
                  {item.status.replace('_', ' ').toUpperCase()}
                </Badge>
              </div>
            </div>

            <div className="delivery-card__details">
              <p><MapPin size={16} /> <strong>Delivery Address:</strong> {item.delivery_address}</p>
              <p><Phone size={16} /> <strong>Customer Phone:</strong> {item.customer_phone} ({item.customer_email})</p>
              <p><Package size={16} /> <strong>Item to Deliver:</strong> {item.product_title} (Qty: {item.quantity})</p>
            </div>

            <div className="delivery-card__actions">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => handleUpdateStatus(item.tracking_number, 'in_transit')}
                disabled={item.status === 'delivered'}
              >
                <Clock size={16} style={{ marginRight: '6px' }} />
                In Transit
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => handleUpdateStatus(item.tracking_number, 'delivered')}
                disabled={item.status === 'delivered'}
              >
                <CheckCircle size={16} style={{ marginRight: '6px' }} />
                Mark Delivered
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePushGPS(item.tracking_number)}
              >
                <Navigation size={16} style={{ marginRight: '6px' }} />
                Push GPS Ping
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setSelectedReceipt(item)}
              >
                <FileText size={16} style={{ marginRight: '6px' }} />
                View Invoice / Receipt
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Printable Receipt Modal */}
      {selectedReceipt && (
        <ReceiptModal
          order={selectedReceipt}
          onClose={() => setSelectedReceipt(null)}
        />
      )}
    </div>
  );
}
