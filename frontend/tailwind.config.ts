import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#1a1a1a",
          light: "#2d2d2d",
          muted: "#6b6b6b",
        },
        paper: {
          DEFAULT: "#faf8f5",
          warm: "#f5f2eb",
          dark: "#e8e4dd",
        },
        vermillion: {
          DEFAULT: "#c94043",
          light: "#e0585b",
          dark: "#a33033",
        },
      },
      fontFamily: {
        sans: ["'Noto Sans SC'", "system-ui", "sans-serif"],
        serif: ["'Noto Serif SC'", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};

export default config;