/**
 * Skeleton loading placeholder with shimmer animation.
 */
import './Skeleton.css';

export function Skeleton({ width, height, radius = 'md', className = '' }) {
  return (
    <div
      className={`skeleton skeleton--${radius} ${className}`}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

export function SkeletonText({ lines = 3, className = '' }) {
  return (
    <div className={`skeleton-text ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton skeleton--sm"
          style={{ width: i === lines - 1 ? '60%' : '100%', height: '14px' }}
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className = '' }) {
  return (
    <div className={`skeleton-card ${className}`} aria-hidden="true">
      <Skeleton width="100%" height="200px" radius="lg" />
      <div className="skeleton-card__body">
        <Skeleton width="75%" height="16px" />
        <Skeleton width="40%" height="14px" />
        <Skeleton width="30%" height="20px" />
      </div>
    </div>
  );
}
