/**
 * MainLayout — wraps all authenticated pages with Header and Footer.
 */
import { Outlet } from 'react-router-dom';
import Header from '../components/organisms/Header';
import './MainLayout.css';

export default function MainLayout() {
  return (
    <div className="main-layout">
      <Header />
      <main className="main-layout__content">
        <Outlet />
      </main>
      <footer className="main-layout__footer">
        <div className="container">
          <p>&copy; 2024 E-Shop Marketplace. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
