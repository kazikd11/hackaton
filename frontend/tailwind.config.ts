import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#181713",
        sand: "#f5efe5",
        paper: "#fbf7ef",
        teal: "#0f766e",
        rust: "#a24b2a",
      },
      fontFamily: {
        sans: ["Aptos", "Segoe UI Variable", "Segoe UI", "sans-serif"],
        display: ["Iowan Old Style", "Georgia", "serif"],
        mono: ["Cascadia Mono", "Consolas", "monospace"],
      },
      boxShadow: {
        soft: "0 20px 60px rgba(24, 23, 19, 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;
