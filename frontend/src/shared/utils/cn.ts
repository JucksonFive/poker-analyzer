/**
 * Tiny utility for conditionally joining CSS class names.
 * Replacement for the `clsx` package — simple, zero-dep.
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}
