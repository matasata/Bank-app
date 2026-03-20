/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        burgundy: '#722F37',
        gold: '#C9A94E',
        parchment: '#F5E6C8',
        inkBlack: '#1A1A2E',
        forestGreen: '#2D5016',
        darkWood: '#3E2723',
      },
      fontFamily: {
        display: ['Cinzel', 'serif'],
        body: ['Crimson Text', 'serif'],
      },
      backgroundImage: {
        'parchment-texture': "linear-gradient(135deg, #F5E6C8 0%, #E8D5A8 50%, #F5E6C8 100%)",
        'dark-leather': "linear-gradient(135deg, #3E2723 0%, #2C1B18 50%, #3E2723 100%)",
      },
      boxShadow: {
        'inset-parchment': 'inset 0 0 30px rgba(62, 39, 35, 0.3)',
        'gold-glow': '0 0 10px rgba(201, 169, 78, 0.5)',
        'panel': '0 4px 20px rgba(0, 0, 0, 0.5)',
      },
      animation: {
        'dice-roll': 'diceRoll 0.6s ease-out',
        'dice-bounce': 'diceBounce 0.4s ease-out',
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
      },
      keyframes: {
        diceRoll: {
          '0%': { transform: 'rotateX(0deg) rotateY(0deg)' },
          '50%': { transform: 'rotateX(180deg) rotateY(180deg)' },
          '100%': { transform: 'rotateX(360deg) rotateY(360deg)' },
        },
        diceBounce: {
          '0%': { transform: 'scale(1.3)', opacity: '0' },
          '50%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(201, 169, 78, 0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(201, 169, 78, 0.6)' },
        },
      },
    },
  },
  plugins: [],
};
