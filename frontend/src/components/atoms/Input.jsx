/**
 * Input component — text, email, password, search variants.
 * Includes label, error message, and focus ring.
 */
import { useState } from 'react';
import { Eye, EyeOff, Search } from 'lucide-react';
import './Input.css';

export default function Input({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  helperText,
  required = false,
  disabled = false,
  icon: Icon,
  id,
  name,
  className = '',
  ...props
}) {
  const [showPassword, setShowPassword] = useState(false);
  const inputId = id || name || label?.toLowerCase().replace(/\s+/g, '-');
  const inputType = type === 'password' && showPassword ? 'text' : type;
  const isSearch = type === 'search';

  return (
    <div className={`input-group ${error ? 'input-group--error' : ''} ${className}`}>
      {label && (
        <label htmlFor={inputId} className="input-group__label">
          {label}
          {required && <span className="input-group__required" aria-hidden="true">*</span>}
        </label>
      )}
      <div className="input-group__wrapper">
        {(Icon || isSearch) && (
          <span className="input-group__icon input-group__icon--left">
            {isSearch ? <Search size={18} /> : <Icon size={18} />}
          </span>
        )}
        <input
          id={inputId}
          name={name}
          type={inputType}
          className={`input-group__input ${Icon || isSearch ? 'input-group__input--has-icon' : ''} ${type === 'password' ? 'input-group__input--has-action' : ''}`}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          required={required}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
          {...props}
        />
        {type === 'password' && (
          <button
            type="button"
            className="input-group__icon input-group__icon--right input-group__toggle"
            onClick={() => setShowPassword(!showPassword)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            tabIndex={-1}
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      {error && (
        <p id={`${inputId}-error`} className="input-group__error" role="alert">
          {error}
        </p>
      )}
      {helperText && !error && (
        <p id={`${inputId}-helper`} className="input-group__helper">
          {helperText}
        </p>
      )}
    </div>
  );
}
