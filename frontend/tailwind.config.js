/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F6F7F5",
        ink: "#1B2430",
        "ink-soft": "#4B5563",
        line: "#DADFE3",
        teal: "#0F766E",
        "teal-soft": "#CCEAE6",
        amber: "#B45309",
        "amber-soft": "#F5DCC0",
        rust: "#B91C1C",
      },
      fontFamily: {
        serif: ["Georgia", "Cambria", "Times New Roman", "serif"],
        sans: [
          "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto",
          "Helvetica Neue", "Arial", "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
