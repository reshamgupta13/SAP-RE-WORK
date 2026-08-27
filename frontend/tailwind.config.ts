import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        rework: {
          slate: "#1e293b",
          accent: "#0f766e",
        },
      },
    },
  },
  plugins: [],
};

export default config;
