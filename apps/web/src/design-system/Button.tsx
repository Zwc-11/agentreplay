import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export function Button({ variant = "primary", className = "", ...rest }: Props) {
  const base = "px-3 py-1.5 rounded-lg text-sm font-medium transition-colors";
  const styles =
    variant === "primary"
      ? "bg-white/90 text-ink hover:bg-white"
      : "bg-white/5 text-gray-200 hover:bg-white/10 border border-white/10";
  return <button className={`${base} ${styles} ${className}`} {...rest} />;
}
