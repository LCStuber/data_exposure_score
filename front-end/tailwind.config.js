/** @type {import('tailwindcss').Config} */
const { fontFamily } = require('tailwindcss/defaultTheme') // Importe o tema padrão

module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      // Adicione esta seção de fontFamily
      fontFamily: {
        sans: ['var(--font-geist-sans)', ...fontFamily.sans],
        mono: ['var(--font-geist-mono)', ...fontFamily.mono],
      },
    },
  },
  plugins: [],
}