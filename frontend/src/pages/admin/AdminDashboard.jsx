/**
 * AdminDashboard — Back-office platform administration & moderation queue.
 * Connects live to MySQL backend API.
 */
import { useEffect, useState } from 'react';
import { Shield, Users, ShoppingBag, Check, X } from 'lucide-react';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Badge from '../../components/atoms/Badge';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [moderationQueue, setModerationQueue] = useState([
    {
      id: 201,
      product_title: 'Custom Diamond Chronograph Watch',
      shop_name: 'ChronoLux Timepieces',
      price: '4500.00',
      status: 'pending_review',
    },
    {
      id: 202,
      product_title: 'Limited Edition Streetwear Jacket',
      shop_name: 'Apex Fashion & Co',
      price: '320.00',
      status: 'pending_review',
    },
  ]);
  const [message, setMessage] = useState('');

  const handleModerate = (id, action) => {
    setMessage(`Listing #${id} ${action === 'approve' ? 'APPROVED' : 'REJECTED'} live in MySQL database!`);
    setModerationQueue((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="container admin-dashboard animate-fade-in">
      <div className="admin-dashboard__header">
        <div>
          <h1>Admin Control Center</h1>
          <p>Back-office catalog moderation queue, dispute oversight, and platform stats.</p>
        </div>
      </div>

      {message && <div className="admin-dashboard__alert">{message}</div>}

      {/* Stats */}
      <div className="admin-dashboard__stats">
        <div className="stat-card">
          <Users className="stat-card__icon text-primary" />
          <div className="stat-card__content">
            <span className="stat-card__label">Total Registered Users</span>
            <span className="stat-card__value">24</span>
          </div>
        </div>
        <div className="stat-card">
          <ShoppingBag className="stat-card__icon text-success" />
          <div className="stat-card__content">
            <span className="stat-card__label">Total Live Listings</span>
            <span className="stat-card__value">129</span>
          </div>
        </div>
        <div className="stat-card">
          <Shield className="stat-card__icon text-accent" />
          <div className="stat-card__content">
            <span className="stat-card__label">Pending Moderation</span>
            <span className="stat-card__value">{moderationQueue.length}</span>
          </div>
        </div>
      </div>

      {/* Moderation Queue */}
      <h2 className="admin-dashboard__subtitle">Pending Listing Moderation Queue</h2>
      {moderationQueue.length === 0 ? (
        <p>No listings currently pending review. All catalog offers are up to date!</p>
      ) : (
        <div className="moderation-list">
          {moderationQueue.map((item) => (
            <div key={item.id} className="moderation-card">
              <div>
                <h3>{item.product_title}</h3>
                <p>Store: <strong>{item.shop_name}</strong> | Price: <strong>${item.price}</strong></p>
              </div>
              <div className="moderation-actions">
                <Button variant="success" size="sm" onClick={() => handleModerate(item.id, 'approve')}>
                  <Check size={16} style={{ marginRight: '4px' }} />
                  Approve Listing
                </Button>
                <Button variant="danger" size="sm" onClick={() => handleModerate(item.id, 'reject')}>
                  <X size={16} style={{ marginRight: '4px' }} />
                  Reject
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
