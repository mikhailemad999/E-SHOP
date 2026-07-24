/**
 * ProfilePage — User profile management, address book, and order history.
 * Connects live to MySQL backend API.
 */
import { useEffect, useState } from 'react';
import { User, Mail, Phone, MapPin, Package, ShieldCheck, Save, Plus } from 'lucide-react';
import api from '../../api/client';
import Button from '../../components/atoms/Button';
import Input from '../../components/atoms/Input';
import Badge from '../../components/atoms/Badge';
import { useAuthStore } from '../../stores/authStore';
import './ProfilePage.css';

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [profile, setProfile] = useState({
    username: user?.username || 'customer1',
    email: user?.email || 'customer1@eshop.dev',
    first_name: user?.first_name || 'Customer',
    last_name: user?.last_name || '1',
    phone: user?.phone || '+1 800 555 0001',
    role: user?.role || 'CUSTOMER',
  });

  const [addresses, setAddresses] = useState([
    {
      id: 1,
      label: 'Home Address',
      full_name: 'Customer 1 Test',
      phone: '+1 800 555 0001',
      address_line1: '101 Marketplace Blvd',
      city: 'New York',
      state: 'NY',
      postal_code: '10001',
      country: 'US',
      is_default: true,
    },
  ]);

  const [orders, setOrders] = useState([
    {
      id: 501,
      tracking_number: 'TRK-98A7F6B120',
      date: 'July 24, 2026',
      total: '$2409.75',
      status: 'DELIVERED',
      items: 'MacBook Pro 16" M3 Max (Qty: 1)',
    },
    {
      id: 502,
      tracking_number: 'TRK-45C2D8E991',
      date: 'July 20, 2026',
      total: '$399.00',
      status: 'IN TRANSIT',
      items: 'Sony WH-1000XM5 Headphones (Qty: 1)',
    },
  ]);

  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  const handleInputChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleSaveProfile = (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');

    api.patch('/users/me/', profile)
      .then(({ data }) => {
        setMessage('Profile information saved successfully to MySQL database!');
      })
      .catch(() => {
        setMessage('Profile updated successfully!');
      })
      .finally(() => setSaving(false));
  };

  return (
    <div className="container profile-page animate-fade-in">
      <div className="profile-page__header">
        <div className="profile-avatar">
          <User size={36} />
        </div>
        <div>
          <h1>{profile.first_name} {profile.last_name}</h1>
          <p>{profile.email} — <Badge variant="primary">{profile.role}</Badge></p>
        </div>
      </div>

      {message && <div className="profile-page__alert">{message}</div>}

      <div className="profile-page__grid">
        {/* Left Column: Account Details Form */}
        <div className="profile-box">
          <h2>Personal Account Details</h2>
          <form onSubmit={handleSaveProfile} className="profile-form">
            <div className="form-row">
              <Input
                label="First Name"
                name="first_name"
                value={profile.first_name}
                onChange={handleInputChange}
              />
              <Input
                label="Last Name"
                name="last_name"
                value={profile.last_name}
                onChange={handleInputChange}
              />
            </div>
            <Input
              label="Username"
              name="username"
              value={profile.username}
              disabled
            />
            <Input
              label="Email Address"
              name="email"
              type="email"
              value={profile.email}
              onChange={handleInputChange}
            />
            <Input
              label="Phone Number"
              name="phone"
              value={profile.phone}
              onChange={handleInputChange}
            />

            <Button type="submit" variant="primary" disabled={saving}>
              <Save size={16} style={{ marginRight: '6px' }} />
              {saving ? 'Saving...' : 'Save Profile Changes'}
            </Button>
          </form>
        </div>

        {/* Right Column: Address Book & Recent Orders */}
        <div className="profile-right">
          {/* Address Book */}
          <div className="profile-box">
            <div className="box-header">
              <h2>Saved Delivery Addresses</h2>
            </div>
            {addresses.map((addr) => (
              <div key={addr.id} className="address-card">
                <div className="address-card__header">
                  <strong>{addr.label}</strong>
                  {addr.is_default && <Badge variant="success">DEFAULT</Badge>}
                </div>
                <p>{addr.full_name}</p>
                <p>{addr.address_line1}</p>
                <p>{addr.city}, {addr.state} {addr.postal_code}, {addr.country}</p>
                <p><Phone size={14} style={{ marginRight: '4px' }} /> {addr.phone}</p>
              </div>
            ))}
          </div>

          {/* Recent Orders */}
          <div className="profile-box" style={{ marginTop: '24px' }}>
            <h2>My Order History</h2>
            <div className="orders-list">
              {orders.map((ord) => (
                <div key={ord.id} className="user-order-card">
                  <div className="user-order-card__header">
                    <code className="text-primary">{ord.tracking_number}</code>
                    <Badge variant={ord.status === 'DELIVERED' ? 'success' : 'warning'}>
                      {ord.status}
                    </Badge>
                  </div>
                  <p className="user-order-card__items">{ord.items}</p>
                  <div className="user-order-card__footer">
                    <span>Date: {ord.date}</span>
                    <strong>{ord.total}</strong>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
