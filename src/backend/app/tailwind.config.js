/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        utb: {
          DEFAULT: '#1E40AF',
        }
      }
    },
  },
  plugins: [],
}