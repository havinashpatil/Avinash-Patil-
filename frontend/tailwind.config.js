/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Medical theme colors
        primary: {
          50: '#e6f2ff',
          100: '#bfdeff',
          200: '#99caff',
          300: '#73b6ff',
          400: '#4da2ff',
          500: '#2e8fff', // Main blue
          600: '#1a75db',
          700: '#115bb7',
          800: '#0a4193',
          900: '#05286f',
        },
        success: {
          50: '#e6f9f5',
          100: '#b3ede0',
          200: '#80e1cb',
          300: '#4dd5b6',
          400: '#1ac9a1',
          500: '#00b894', // Main green
          600: '#009a7a',
          700: '#007c60',
          800: '#005e46',
          900: '#00402c',
        },
        danger: {
          50: '#ffe6e6',
          100: '#ffb3b3',
          200: '#ff8080',
          300: '#ff4d4d',
          400: '#ff1a1a',
          500: '#e60000', // Main red
          600: '#b30000',
          700: '#800000',
          800: '#4d0000',
          900: '#1a0000',
        },
        warning: {
          50: '#fff8e6',
          100: '#ffeeb3',
          200: '#ffe480',
          300: '#ffda4d',
          400: '#ffd01a',
          500: '#ffc600',
          600: '#cc9e00',
          700: '#997600',
          800: '#664f00',
          900: '#332700',
        },
        neutral: {
          50: '#f8f9fa',
          100: '#f1f3f5',
          200: '#e9ecef',
          300: '#dee2e6',
          400: '#ced4da',
          500: '#adb5bd',
          600: '#868e96',
          700: '#495057',
          800: '#343a40',
          900: '#212529',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
        'glow': '0 0 20px rgba(46, 143, 255, 0.3)',
        'glow-success': '0 0 20px rgba(0, 184, 148, 0.3)',
        'glow-danger': '0 0 20px rgba(230, 0, 0, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(230, 0, 0, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(230, 0, 0, 0.6)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
