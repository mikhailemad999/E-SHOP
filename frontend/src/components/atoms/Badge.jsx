/**
 * Badge component — status indicators with semantic colors.
 */
import './Badge.css';

const VARIANT_MAP = {
  live: 'success',
  accepted: 'success',
  delivered: 'success',
  completed: 'success',
  pending: 'warning',
  pending_review: 'warning',
  processing: 'warning',
  packed: 'info',
  shipped: 'info',
  in_transit: 'info',
  rejected: 'danger',
  denied: 'danger',
  failed: 'danger',
  cancelled: 'danger',
  out_of_stock: 'neutral',
  draft: 'neutral',
  archived: 'neutral',
};

export default function Badge({
  children,
  variant,
  status,
  size = 'sm',
  dot = false,
  className = '',
}) {
  const resolvedVariant = variant || VARIANT_MAP[status] || 'neutral';

  return (
    <span className={`badge badge--${resolvedVariant} badge--${size} ${className}`}>
      {dot && <span className="badge__dot" aria-hidden="true" />}
      {children || (status && status.replace(/_/g, ' '))}
    </span>
  );
}
