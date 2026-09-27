/**
 * E-Shop Marketplace — Root App Component
 * Role-aware routing with ProtectedRoute security for dashboards and Shopping Cart page.
 */
import { Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/atoms/ProtectedRoute';

// Layouts
import MainLayout from './layouts/MainLayout';

// Pages
import HomePage from './pages/customer/HomePage';
import SearchPage from './pages/customer/SearchPage';
import ProductDetailPage from './pages/customer/ProductDetailPage';
import CartPage from './pages/customer/CartPage';
import ProfilePage from './pages/customer/ProfilePage';
import WishlistPage from './pages/customer/WishlistPage';
import TrackingPage from './pages/customer/TrackingPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import SellerDashboard from './pages/seller/SellerDashboard';
import DeliveryManagerDashboard from './pages/delivery/DeliveryManagerDashboard';
import DeliveryAgentDashboard from './pages/delivery/DeliveryAgentDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';

export default function App() {
  return (
    <Routes>
      {/* Public auth routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Main layout with header/footer */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="products/:slug" element={<ProductDetailPage />} />
        <Route path="products/:slug/" element={<ProductDetailPage />} />
        <Route path="cart" element={<CartPage />} />
        <Route path="wishlist" element={<WishlistPage />} />
        <Route path="track/:trackingNumber" element={<TrackingPage />} />

        {/* Protected Customer Profile */}
        <Route
          path="profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />

        {/* Dedicated Admin Route */}
        <Route
          path="admin"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'SUPER_ADMIN']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={['ADMIN', 'SUPER_ADMIN']}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        {/* Dedicated Seller Route */}
        <Route
          path="seller"
          element={
            <ProtectedRoute allowedRoles={['SELLER', 'SUPER_ADMIN']}>
              <SellerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="seller/dashboard"
          element={
            <ProtectedRoute allowedRoles={['SELLER', 'SUPER_ADMIN']}>
              <SellerDashboard />
            </ProtectedRoute>
          }
        />

        {/* Dedicated Delivery Routes */}
        <Route
          path="delivery"
          element={
            <ProtectedRoute allowedRoles={['DELIVERY_MANAGER', 'SUPER_ADMIN']}>
              <DeliveryManagerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="delivery/manager"
          element={
            <ProtectedRoute allowedRoles={['DELIVERY_MANAGER', 'SUPER_ADMIN']}>
              <DeliveryManagerDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="delivery/agent"
          element={
            <ProtectedRoute allowedRoles={['DELIVERY_AGENT', 'SUPER_ADMIN']}>
              <DeliveryAgentDashboard />
            </ProtectedRoute>
          }
        />

        {/* Wildcard catch-all fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
