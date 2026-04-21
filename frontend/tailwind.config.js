/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0891B2',
        'primary-light': '#22D3EE',
        'primary-dark': '#0E7490',
        accent: '#059669',
        'accent-light': '#34D399',

        'bg-primary': '#F8FAFC',
        'bg-secondary': '#FFFFFF',
        'bg-card': '#FFFFFF',
        'bg-hover': '#F1F5F9',

        'text-primary': '#1E293B',
        'text-body': '#475569',
        'text-secondary': '#94A3B8',
        'text-muted': '#CBD5E1',

        success: '#059669',
        warning: '#F59E0B',
        danger: '#EF4444',
        info: '#0284C7',
      },
      fontFamily: {
        sans: ['Noto Sans SC', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      borderColor: {
        DEFAULT: '#E2E8F0',
        hover: '#CBD5E1',
      },
    },
  },
  plugins: [],
}
