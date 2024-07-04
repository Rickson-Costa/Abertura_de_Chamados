/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [ './templates/**/*.html', './main/templates/*.html','./node_modules/flowbite/**/*.js' ],
  theme: {
    extend: {},
  },
  plugins: [require('flowbite/plugin')],
}

