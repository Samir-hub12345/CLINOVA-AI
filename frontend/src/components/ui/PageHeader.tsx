import React from "react";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  badge,
  actions,
  breadcrumbs,
}) => {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 8,
        marginBottom: "var(--clinova-space-6)",
        borderBottom: "1px solid var(--clinova-border)",
        paddingBottom: "var(--clinova-space-4)",
      }}
    >
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav aria-label="Breadcrumb" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.75rem", color: "var(--clinova-text-muted)" }}>
          {breadcrumbs.map((b, i) => (
            <React.Fragment key={i}>
              {i > 0 && <span>/</span>}
              {b.href ? (
                <a href={b.href} style={{ color: "var(--clinova-text-muted)", textDecoration: "none" }}>
                  {b.label}
                </a>
              ) : (
                <span style={{ color: "var(--clinova-text-primary)", fontWeight: 600 }}>{b.label}</span>
              )}
            </React.Fragment>
          ))}
        </nav>
      )}

      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <h1>{title}</h1>
          {badge}
        </div>
        {actions && <div style={{ display: "flex", alignItems: "center", gap: 8 }}>{actions}</div>}
      </div>

      {subtitle && <p style={{ fontSize: "0.875rem", maxWidth: 900 }}>{subtitle}</p>}
    </div>
  );
};

export const SectionHeader: React.FC<{
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}> = ({ title, subtitle, action }) => {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "var(--clinova-space-3)",
      }}
    >
      <div>
        <h3 style={{ fontSize: "1.0625rem" }}>{title}</h3>
        {subtitle && <p style={{ fontSize: "0.75rem" }}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};
