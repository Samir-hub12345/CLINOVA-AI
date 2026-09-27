import React from "react";
import Image from "next/image";
import Link from "next/link";

export type LogoVariant = "full" | "mark" | "badge" | "horizontal";
export type LogoSize = "xs" | "sm" | "md" | "lg" | "xl";
export type LogoTheme = "light" | "dark";

export interface ClinovaLogoProps {
  variant?: LogoVariant;
  size?: LogoSize;
  theme?: LogoTheme;
  showTagline?: boolean;
  taglineText?: string;
  className?: string;
  markClassName?: string;
  textClassName?: string;
  href?: string;
  priority?: boolean;
  alt?: string;
}

const SIZE_MAP: Record<LogoSize, { mark: number; text: string; subText: string; gap: string }> = {
  xs: { mark: 22, text: "text-xs", subText: "text-[9px]", gap: "gap-1.5" },
  sm: { mark: 28, text: "text-sm", subText: "text-[10px]", gap: "gap-2" },
  md: { mark: 36, text: "text-base", subText: "text-[11px]", gap: "gap-2.5" },
  lg: { mark: 48, text: "text-xl", subText: "text-xs", gap: "gap-3" },
  xl: { mark: 64, text: "text-2xl sm:text-3xl", subText: "text-xs sm:text-sm", gap: "gap-4" },
};

export const ClinovaLogo: React.FC<ClinovaLogoProps> = ({
  variant = "full",
  size = "md",
  theme = "light",
  showTagline = false,
  taglineText = "Clinical Decision Support",
  className = "",
  markClassName = "",
  textClassName = "",
  href,
  priority = false,
  alt = "Clinova AI",
}) => {
  const config = SIZE_MAP[size] || SIZE_MAP.md;
  const isDark = theme === "dark";

  // Mark Image Source
  const markSrc =
    variant === "badge"
      ? "/branding/clinova-ai-badge.png"
      : "/branding/clinova-ai-mark.png";

  const renderMark = () => (
    <div
      className={`relative flex items-center justify-center shrink-0 transition-transform duration-200 group-hover:scale-105 ${markClassName}`}
      style={{ width: config.mark, height: config.mark }}
    >
      <Image
        src={markSrc}
        alt={alt}
        width={config.mark}
        height={config.mark}
        priority={priority}
        className="w-full h-full object-contain drop-shadow-xs"
      />
    </div>
  );

  const renderText = () => (
    <div className={`flex flex-col leading-none select-none ${textClassName}`}>
      <span
        className={`font-black tracking-tight ${config.text} ${
          isDark ? "text-white" : "text-slate-900"
        }`}
      >
        CLINOVA{" "}
        <span className={isDark ? "text-teal-400" : "text-teal-600"}>AI</span>
      </span>
      {showTagline && (
        <span
          className={`font-medium tracking-wide uppercase mt-1 ${config.subText} ${
            isDark ? "text-slate-400" : "text-slate-500"
          }`}
        >
          {taglineText}
        </span>
      )}
    </div>
  );

  const content = (
    <div
      className={`inline-flex items-center ${
        variant === "mark" || variant === "badge" ? "" : config.gap
      } ${className}`}
    >
      {renderMark()}
      {variant !== "mark" && variant !== "badge" && renderText()}
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="group inline-flex items-center focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 rounded-lg">
        {content}
      </Link>
    );
  }

  return content;
};

// Default export for standard import patterns
export default ClinovaLogo;
