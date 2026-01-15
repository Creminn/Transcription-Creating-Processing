/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Solar gradient colors
        solar: {
          start: '#E92E2F',
          end: '#FF6126',
        },
        // Eclipse gradient colors
        eclipse: {
          start: '#261A28',
          end: '#18181B',
        },
        // Lunar gradient colors
        lunar: {
          start: '#EFEBE4',
          end: '#D0C2C7',
        },
        // Celestial gradient colors
        celestial: {
          start: '#2EDFE2',
          end: '#71F3A7',
        },
        // Stratos gradient colors
        stratos: {
          start: '#44221E',
          end: '#18181B',
        },
        // Cosmic gradient colors
        cosmic: {
          start: '#EFEBE4',
          end: '#F0CABF',
        },
        // Orbit gradient colors
        orbit: {
          start: '#23423D',
          end: '#18181B',
        },
        // Stardust gradient colors
        stardust: {
          start: '#EFEBE4',
          end: '#CFEBDD',
        },
      },
      backgroundImage: {
        'gradient-solar': 'linear-gradient(135deg, #E92E2F, #FF6126)',
        'gradient-eclipse': 'linear-gradient(135deg, #261A28, #18181B)',
        'gradient-lunar': 'linear-gradient(135deg, #EFEBE4, #D0C2C7)',
        'gradient-celestial': 'linear-gradient(135deg, #2EDFE2, #71F3A7)',
        'gradient-stratos': 'linear-gradient(135deg, #44221E, #18181B)',
        'gradient-cosmic': 'linear-gradient(135deg, #EFEBE4, #F0CABF)',
        'gradient-orbit': 'linear-gradient(135deg, #23423D, #18181B)',
        'gradient-stardust': 'linear-gradient(135deg, #EFEBE4, #CFEBDD)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-20px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
