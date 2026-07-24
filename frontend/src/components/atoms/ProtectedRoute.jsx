/**
 * ProtectedRoute component — enforces authentication and role-based access.
 * Redirects unauthenticated users to /login.
 */
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

export default function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname)}`} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0 && user && !allowedRoles.includes(user.role)) {
    return (
      <div className="container" style={{ padding: '60px 20px', textAlign: 'center' }}>
        <h2>Access Restricted</h2>
        <p>Your account role ({user.role}) does not have permission to view this dashboard.</p>
      </div>
    );
  }

  return children;
}
