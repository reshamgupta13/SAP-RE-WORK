import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        ivory: "var(--color-ivory)",
        parchment: "var(--color-parchment)",
        navy: "var(--color-navy)",
        sage: "var(--color-sage)",
        "sage-muted": "var(--color-sage-muted)",
        ocean: "var(--color-ocean)",
        amber: "var(--color-amber)",
        ink: "var(--color-ink)",
        muted: "var(--color-muted)",
        surface: "var(--color-surface)",
        "surface-raised": "var(--color-surface-raised)",
        border: "var(--color-border)",
        accent: "var(--color-accent)",
        "accent-hover": "var(--color-accent-hover)",
      },
      fontFamily: {
        display: ["var(--font-display)", "Georgia", "serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        ui: ["var(--font-ui)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        soft: "var(--shadow-soft)",
        lift: "var(--shadow-lift)",
        card: "var(--shadow-card)",
      },
      transitionDuration: {
        micro: "80ms",
        interaction: "140ms",
        standard: "220ms",
        section: "360ms",
        hero: "650ms",
      },
      animation: {
        "hero-reveal": "heroReveal 650ms cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "fade-up": "fadeUp 360ms cubic-bezier(0.22, 1, 0.36, 1) forwards",
        drift: "drift 28s ease-in-out infinite alternate",
      },
      keyframes: {
        heroReveal: {
          from: { opacity: "0", transform: "translateX(-1.25rem)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        fadeUp: {
          from: { opacity: "0", transform: "translateY(0.75rem)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        drift: {
          from: { transform: "translate(0, 0)" },
          to: { transform: "translate(12px, -8px)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
