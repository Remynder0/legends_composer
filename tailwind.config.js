/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        apex: {
          red: '#da292a',
          dark: '#1a1a1a',
          darker: '#111111',
          gray: '#2c2c2c',
        }
      }
    },
  },
  plugins: [],
}
