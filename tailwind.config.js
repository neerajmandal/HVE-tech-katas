/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  safelist: [
    'bg-teal-100', 'bg-teal-500', 'bg-teal-600', 'bg-teal-700',
    'bg-cyan-100', 'bg-cyan-500', 'bg-cyan-600',
    'bg-sky-100', 'bg-sky-600',
    'bg-amber-100', 'bg-amber-500',
    'bg-red-100', 'bg-red-600',
    'bg-green-100', 'bg-green-600',
    'bg-purple-100', 'bg-purple-600',
    'bg-slate-700', 'bg-slate-800', 'bg-slate-900',
    'text-teal-400', 'text-teal-600', 'text-teal-700',
    'text-cyan-400', 'text-cyan-600',
    'text-sky-600', 'text-sky-700',
    'text-amber-600', 'text-amber-700',
    'text-red-600', 'text-red-700',
    'text-green-600', 'text-green-700',
    'text-purple-600', 'text-purple-700',
    'text-slate-300', 'text-slate-400',
    'border-teal-500', 'border-slate-700',
    'ring-teal-500',
    'focus:ring-teal-500', 'focus:ring-teal-300',
    'focus:border-teal-500',
    'hover:bg-teal-700', 'hover:text-teal-600',
    'bg-rose-600', 'bg-indigo-600', 'bg-emerald-600',
    'bg-violet-600', 'bg-fuchsia-600',
    'border-rose-600', 'border-indigo-600', 'border-emerald-600',
    'border-violet-600', 'border-fuchsia-600',
    'text-rose-600', 'text-indigo-600', 'text-emerald-600',
    'text-emerald-900', 'text-violet-600', 'text-fuchsia-600',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#0d9488',   // teal-600
          secondary: '#0f766e', // teal-700
          accent: '#06b6d4',    // cyan-500
        }
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
  ],
}
