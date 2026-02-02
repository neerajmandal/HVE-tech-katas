/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  safelist: [
    // Debt calculator color classes
    'bg-rose-600',
    'bg-indigo-600',
    'bg-emerald-600',
    'bg-violet-600',
    'bg-amber-600',
    'bg-fuchsia-600',
    'bg-slate-600',
    'border-rose-600',
    'border-indigo-600',
    'border-emerald-600',
    'border-violet-600',
    'border-amber-600',
    'border-fuchsia-600',
    'border-slate-600',
    'text-rose-600',
    'text-indigo-600',
    'text-emerald-600',
    'text-emerald-900',
    'text-violet-600',
    'text-amber-600',
    'text-fuchsia-600',
    'text-slate-600',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#059669', // emerald-600
          secondary: '#047857', // emerald-700
          accent: '#115e59', // teal-800
        }
      },
      backgroundImage: {
        //bg-gradient-to-b from-emerald-900 via-emerald-800 to-emerald-950
        'brand-gradient': 'linear-gradient(to bottom, rgb(6, 78, 59), rgb(6, 95, 70), rgb(2, 44, 34))',
      }
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
}