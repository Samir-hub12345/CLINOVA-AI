"use client";

import React from "react";
import { cn } from "@/lib/utils";

export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  label: string;
}

export const IconButton: React.FC<IconButtonProps> = ({
  children,
  label,
  className,
  ...props
}) => {
  return (
    <button
      className={cn("clinova-icon-btn", className)}
      aria-label={label}
      title={label}
      {...props}
    >
      {children}
    </button>
  );
};
