/**
 * Button component — primary, secondary, ghost, danger variants.
 * 44px min touch target per ui-ux-pro-max accessibility guidelines.
 */
import './Button.css';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  fullWidth = false,
  icon: Icon,
  iconPosition = 'left',
  type = 'button',
  onClick,
  className = '',
  ...props
}) {
  const classes = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    fullWidth && 'btn--full',
    isLoading && 'btn--loading',
    className,
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || isLoading}
      onClick={onClick}
      {...props}
    >
      {isLoading && (
        <span className="btn__spinner" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" opacity="0.25" />
            <path d="M12 2a10 10 0 0 1 10 10" />
          </svg>
        </span>
      )}
      {Icon && iconPosition === 'left' && !isLoading && (
        <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />
      )}
      <span className="btn__label">{children}</span>
      {Icon && iconPosition === 'right' && !isLoading && (
        <Icon size={size === 'sm' ? 14 : size === 'lg' ? 20 : 16} />
      )}
    </button>
  );
}
