/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts,tsx,js,jsx}",
    "./src/app/**/*.{html,ts}",
    "./src/index.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  safelist: [
    'bg-blue-50',
    'bg-green-50', 
    'bg-yellow-50',
    'bg-red-50',
    'text-blue-800',
    'text-green-800',
    'text-yellow-800',
    'text-red-800'
  ]
}