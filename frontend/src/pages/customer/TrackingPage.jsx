/**
 * Customer Live Delivery Tracking Page.
 * Connects to Django Channels WebSocket `ws/delivery/{tracking_number}/`
 * Renders Leaflet / OpenStreetMap with real-time agent position marker.
 */
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Truck, CheckCircle2, Clock, MapPin, AlertCircle } from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/atoms/Badge';
import 'leaflet/dist/leaflet.css';
import './TrackingPage.css';

// Fix Leaflet icon paths
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.setView(center, 15);
  }, [center, map]);
  return null;
}

export default function TrackingPage() {
  const { trackingNumber } = useParams();
  const [assignment, setAssignment] = useState(null);
  const [agentLocation, setAgentLocation] = useState(null);
  const [wsStatus, setWsStatus] = useState('connecting');
  const [error, setError] = useState('');

  // Fetch initial assignment detail
  useEffect(() => {
    api.get(`/delivery/track/${trackingNumber}/`)
      .then(({ data }) => {
        setAssignment(data);
        if (data.latest_ping) {
          setAgentLocation([parseFloat(data.latest_ping.lat), parseFloat(data.latest_ping.lng)]);
        } else {
          // Default fallback location (e.g. city center)
          setAgentLocation([40.7128, -74.0060]);
        }
      })
      .catch(() => setError('Tracking number not found.'));
  }, [trackingNumber]);

  // Connect to Django Channels WebSocket with HTTP polling fallback
  useEffect(() => {
    if (!trackingNumber) return;

    let socket = null;
    let pollInterval = null;

    try {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/delivery/${trackingNumber}/`;
      socket = new WebSocket(wsUrl);

      socket.onopen = () => setWsStatus('connected');
      socket.onclose = () => {
        setWsStatus('disconnected');
        startFallbackPolling();
      };
      socket.onerror = () => {
        setWsStatus('offline fallback');
        startFallbackPolling();
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'location_update') {
          setAgentLocation([parseFloat(data.lat), parseFloat(data.lng)]);
          if (data.status) {
            setAssignment((prev) => (prev ? { ...prev, status: data.status } : prev));
          }
        }
      };
    } catch {
      setWsStatus('offline fallback');
      startFallbackPolling();
    }

    function startFallbackPolling() {
      if (pollInterval) return;
      pollInterval = setInterval(() => {
        api.get(`/delivery/track/${trackingNumber}/`)
          .then(({ data }) => {
            if (data.latest_ping) {
              setAgentLocation([parseFloat(data.latest_ping.lat), parseFloat(data.latest_ping.lng)]);
            }
            if (data.status) {
              setAssignment((prev) => (prev ? { ...prev, status: data.status } : prev));
            }
          })
          .catch(() => {});
      }, 10000);
    }

    return () => {
      if (socket) socket.close();
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [trackingNumber]);

  if (error) {
    return (
      <div className="container tracking-page--error animate-fade-in">
        <AlertCircle size={48} className="tracking-page__error-icon" />
        <h2>{error}</h2>
        <p>Please check your tracking number and try again.</p>
      </div>
    );
  }

  return (
    <div className="container tracking-page animate-fade-in">
      <div className="tracking-page__header">
        <div>
          <span className="tracking-page__subtitle">Live Delivery Tracking</span>
          <h1 className="tracking-page__title">#{trackingNumber}</h1>
        </div>
        <div className="tracking-page__status-badge">
          <Badge status={assignment?.status || 'pending'} size="md" dot />
          <span className={`tracking-page__ws-indicator tracking-page__ws-indicator--${wsStatus}`}>
            ● {wsStatus === 'connected' ? 'Live GPS' : wsStatus}
          </span>
        </div>
      </div>

      <div className="tracking-page__grid">
        {/* Live Map */}
        <div className="tracking-page__map-container">
          {agentLocation && (
            <MapContainer
              center={agentLocation}
              zoom={14}
              scrollWheelZoom={false}
              style={{ height: '100%', width: '100%', borderRadius: 'var(--eshop-radius-2xl)' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <Marker position={agentLocation}>
                <Popup>
                  <strong>Delivery Agent</strong>
                  <br />
                  Status: {assignment?.status || 'In Transit'}
                </Popup>
              </Marker>
              <MapRecenter center={agentLocation} />
            </MapContainer>
          )}
        </div>

        {/* Info Sidebar */}
        <div className="tracking-page__sidebar">
          <div className="tracking-card">
            <h3><Truck size={20} /> Delivery Info</h3>
            <div className="tracking-info__row">
              <span className="tracking-info__label">Agent</span>
              <span className="tracking-info__value">{assignment?.agent_name || 'Assigned Agent'}</span>
            </div>
            <div className="tracking-info__row">
              <span className="tracking-info__label">Contact</span>
              <span className="tracking-info__value">{assignment?.agent_phone || 'N/A'}</span>
            </div>
          </div>

          <div className="tracking-card">
            <h3><Clock size={20} /> Timeline</h3>
            <ul className="timeline">
              <li className={`timeline__item ${assignment?.assigned_at ? 'timeline__item--done' : ''}`}>
                <CheckCircle2 size={16} />
                <div>
                  <strong>Order Assigned</strong>
                  <span>{assignment?.assigned_at ? new Date(assignment.assigned_at).toLocaleTimeString() : 'Pending'}</span>
                </div>
              </li>
              <li className={`timeline__item ${assignment?.picked_up_at ? 'timeline__item--done' : ''}`}>
                <CheckCircle2 size={16} />
                <div>
                  <strong>Picked Up</strong>
                  <span>{assignment?.picked_up_at ? new Date(assignment.picked_up_at).toLocaleTimeString() : 'In progress'}</span>
                </div>
              </li>
              <li className={`timeline__item ${assignment?.delivered_at ? 'timeline__item--done' : ''}`}>
                <CheckCircle2 size={16} />
                <div>
                  <strong>Delivered</strong>
                  <span>{assignment?.delivered_at ? new Date(assignment.delivered_at).toLocaleTimeString() : 'Estimated soon'}</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
