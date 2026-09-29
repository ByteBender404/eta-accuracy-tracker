/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f1115',
        surface: '#1a1d24',
        surfaceHighlight: '#2a2e39',
        amberBase: '#F59E0B',
        tealBase: '#14B8A6',
        success: '#10B981', // emerald-500
        warning: '#F59E0B',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
