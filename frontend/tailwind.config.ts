import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        surface: {
          DEFAULT: '#ffffff',
          2: '#f8fafc',
        },
        ink: {
          DEFAULT: '#0f172a',
          1: '#1e293b',
          2: '#334155',
          3: '#64748b',
          4: '#94a3b8',
          5: '#cbd5e1',
        },
        brand: '#0ea5e9',
        line: '#e2e8f0',
      },
    },
  },
  plugins: [],
}

export default config
