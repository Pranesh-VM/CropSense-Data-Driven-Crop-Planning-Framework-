/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdf4',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
        },
        secondary: {
          400: '#60a5fa',
          500: '#3B82F6',
          600: '#2563eb',
        },
        success: '#22C55E',
        warning: '#EAB308',
        error: '#EF4444',
        critical: '#DC2626',
      },
    },
  },
  plugins: [],
}
