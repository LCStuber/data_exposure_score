/** @type {import('tailwindcss').Config} */
const { fontFamily } = require('tailwindcss/defaultTheme')

module.exports = {
  darkMode: 'class', // Controlamos o tema escuro via classe .dark no <html>
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-geist-sans)', ...fontFamily.sans],
        mono: ['var(--font-geist-mono)', ...fontFamily.mono],
      },
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)'
      }
    },
  },
  plugins: [],
}