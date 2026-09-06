/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Agricultural identity: deep leaf greens, soil browns, sky accents.
        leaf: {
          50: '#f2f8f1',
          100: '#e0efdd',
          200: '#c1dfbd',
          300: '#95c78f',
          400: '#66aa5e',
          500: '#458c3e',
          600: '#2f6f2c',
          700: '#265925',
          800: '#204721',
          900: '#1b3b1d',
        },
        soil: {
          50: '#faf7f2',
          100: '#f1e9dc',
          200: '#e2d2b9',
          300: '#cdb28c',
          400: '#b48f63',
          500: '#9c7549',
          600: '#7f5c3a',
          700: '#654830',
          800: '#523b2b',
          900: '#453226',
        },
        sky: {
          50: '#eff8ff',
          100: '#dbeefe',
          200: '#bfe2fe',
          300: '#93d0fd',
          400: '#60b5fa',
          500: '#3b98f6',
          600: '#257aeb',
          700: '#1d63d8',
          800: '#1e51af',
          900: '#1e468a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(27, 59, 29, 0.04), 0 8px 24px -12px rgba(27, 59, 29, 0.16)',
        lift: '0 2px 4px rgba(27, 59, 29, 0.06), 0 18px 40px -18px rgba(27, 59, 29, 0.28)',
      },
      keyframes: {
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(6px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: { 'fade-up': 'fade-up 0.25s ease-out both' },
    },
  },
  plugins: [],
}
