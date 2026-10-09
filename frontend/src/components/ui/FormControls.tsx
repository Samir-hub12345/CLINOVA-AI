"use client";

import React from "react";
import { Search, X } from "lucide-react";

export interface FormFieldProps {
  label: string;
  htmlFor?: string;
  required?: boolean;
  helpText?: string;
  error?: string;
  children: React.ReactNode;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  htmlFor,
  required,
  helpText,
  error,
  children,
}) => {
  return (
    <div className="clinova-form-group">
      <label className="clinova-form-label" htmlFor={htmlFor}>
        {label}
        {required && <span style={{ color: "var(--clinova-danger)", marginLeft: 4 }}>*</span>}
      </label>
      {children}
      {helpText && !error && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>{helpText}</span>
      )}
      {error && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-danger)", fontWeight: 600 }}>{error}</span>
      )}
    </div>
  );
};

export interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  required?: boolean;
  helpText?: string;
  error?: string;
}

export const TextArea: React.FC<TextAreaProps> = ({
  label,
  required,
  helpText,
  error,
  id,
  className,
  style,
  ...props
}) => {
  const content = (
    <textarea
      id={id}
      className={`clinova-textarea ${className || ""}`}
      style={{
        borderColor: error ? "var(--clinova-danger)" : undefined,
        ...style,
      }}
      aria-invalid={!!error}
      {...props}
    />
  );

  if (label) {
    return (
      <FormField label={label} htmlFor={id} required={required} helpText={helpText} error={error}>
        {content}
      </FormField>
    );
  }

  return (
    <div className="clinova-form-group">
      {content}
      {helpText && !error && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>{helpText}</span>
      )}
      {error && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-danger)", fontWeight: 600 }}>{error}</span>
      )}
    </div>
  );
};

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectFieldProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  required?: boolean;
  helpText?: string;
  error?: string;
  options: SelectOption[];
}

export const SelectField: React.FC<SelectFieldProps> = ({
  label,
  required,
  helpText,
  error,
  options,
  id,
  className,
  style,
  ...props
}) => {
  const content = (
    <select
      id={id}
      className={`clinova-select ${className || ""}`}
      style={{
        borderColor: error ? "var(--clinova-danger)" : undefined,
        ...style,
      }}
      aria-invalid={!!error}
      {...props}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value} disabled={opt.disabled}>
          {opt.label}
        </option>
      ))}
    </select>
  );

  if (label) {
    return (
      <FormField label={label} htmlFor={id} required={required} helpText={helpText} error={error}>
        {content}
      </FormField>
    );
  }

  return (
    <div className="clinova-form-group">
      {content}
      {helpText && !error && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>{helpText}</span>
      )}
      {error && (
        <span style={{ fontSize: "0.75rem", color: "var(--clinova-danger)", fontWeight: 600 }}>{error}</span>
      )}
    </div>
  );
};

export const SearchField: React.FC<{
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
}> = ({ value, onChange, placeholder = "Search by synthetic ID, case number, symptom..." }) => {
  return (
    <div style={{ position: "relative", width: "100%", maxWidth: 360 }}>
      <Search
        style={{
          position: "absolute",
          left: 10,
          top: "50%",
          transform: "translateY(-50%)",
          width: 15,
          height: 15,
          color: "var(--clinova-text-muted)",
          pointerEvents: "none",
        }}
        aria-hidden="true"
      />
      <input
        type="text"
        className="clinova-input"
        style={{ paddingLeft: 32, paddingRight: value ? 32 : 12 }}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Search"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          aria-label="Clear search"
          style={{
            position: "absolute",
            right: 8,
            top: "50%",
            transform: "translateY(-50%)",
            background: "transparent",
            border: "none",
            cursor: "pointer",
            color: "var(--clinova-text-muted)",
            display: "flex",
            alignItems: "center",
          }}
        >
          <X style={{ width: 14, height: 14 }} aria-hidden="true" />
        </button>
      )}
    </div>
  );
};
