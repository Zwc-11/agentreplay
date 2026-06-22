/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Visual identity: near-black, not pure black; premium, not neon.
        ink: "#0a0b0e",
        panel: "#13151a",
        edge: "#1f232b",
        success: "#34d399", // green  — successful path
        failure: "#f87171", // red    — agent divergence
        uncertain: "#fbbf24", // yellow — uncertain state
        ai: "#a78bfa",        // purple — AI summary
      },
    },
  },
  plugins: [],
};
