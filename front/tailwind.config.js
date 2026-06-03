/** @type {import('tailwindcss').Config} */
import { heroui } from "@heroui/react";

export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "secondary-fixed-dim": "#00dbe9",
        "error-container": "#93000a",
        "background": "#080C14",
        "outline": "#8e9192",
        "surface-container-lowest": "#0e0e0e",
        "primary": "#ffffff",
        "on-surface-variant": "#c4c7c8",
        "surface-container-low": "#1c1b1b",
        "on-background": "#e5e2e1",
        "surface-container-high": "#2a2a2a",
        "outline-variant": "#444748",
        "surface-dim": "#141313",
        "on-error": "#690005",
        "on-surface": "#e5e2e1",
        "on-error-container": "#ffdad6",
        "surface-container": "#201f1f",
        "on-secondary": "#00363a",
        "surface": "#141313",
        "secondary-fixed": "#7df4ff",
        "secondary-container": "#00eefc",
        "error": "#ffb4ab",
        "surface-container-highest": "#353434",
      },
      spacing: {
        "xs": "4px",
        "sm": "8px",
        "md": "16px",
        "lg": "24px",
        "xl": "32px",
        "gutter": "20px",
      },
      fontFamily: {
        sans: ["Geist", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [
    heroui({
      themes: {
        dark: {
          colors: {
            background: "#080C14",
            foreground: "#e5e2e1",
            primary: {
              DEFAULT: "#00dbe9",
              foreground: "#080C14",
            },
            secondary: {
              DEFAULT: "#00eefc",
              foreground: "#00363a",
            },
            danger: {
              DEFAULT: "#ffb4ab",
              foreground: "#690005",
            },
            success: {
              DEFAULT: "#00dbe9",
              foreground: "#080C14",
            },
            warning: {
              DEFAULT: "#eab308",
              foreground: "#000",
            },
            focus: "#00dbe9",
          },
        },
      },
    }),
  ],
};
