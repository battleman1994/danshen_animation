import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 奶油基底（Lovable 风格）
        cream: {
          50: '#fef9f0',
          100: '#fdf3e5',
          200: '#f0e6d8',
          300: '#e0d4c3',
        },
        // 文字色阶（基于 #2d2d2d 的透明度变化）
        ink: {
          DEFAULT: '#2d2d2d',
          muted: '#6b6b6b',
          light: '#999999',
        },
        // 渐变主色
        warm: {
          coral: '#ff6b6b',
          peach: '#ffa07a',
          lavender: '#a78bfa',
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'pill': '50px',
      },
      boxShadow: {
        'warm': '0 2px 16px rgba(45, 45, 45, 0.06)',
        'warm-lg': '0 4px 24px rgba(45, 45, 45, 0.08)',
        'inset-button': 'rgba(255,255,255,0.15) 0px 0.5px 0px 0px inset, rgba(0,0,0,0.15) 0px 0px 0px 0.5px inset, rgba(0,0,0,0.05) 0px 1px 2px 0px',
        'focus-warm': '0 0 0 3px rgba(255, 107, 107, 0.2)',
      },
      animation: {
        'gradient-shift': 'gradientShift 8s ease infinite',
        'float': 'float 4s ease-in-out infinite',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
      backgroundSize: {
        '300%': '300% 300%',
      },
    },
  },
  plugins: [],
}

export default config
