import { type ClassValue, clsx } from "clsx";

/**
 * Standard class name combiner using clsx.
 * Pure CSS / CSS Modules architecture.
 */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}
