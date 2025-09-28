/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'mono': [
          'JetBrains Mono',
          'SF Mono',
          'Monaco',
          'Menlo',
          'Consolas',
          'Liberation Mono',
          'Courier New',
          'monospace'
        ],
        'sans': [
          'JetBrains Mono',
          'SF Mono',
          'Monaco',
          'monospace'
        ]
      },
      fontWeight: {
        'normal': '500',
        'medium': '600', 
        'bold': '800',
        '500': '500',
        '600': '600',
        '800': '800'
      },
      colors: {
        // The Monospace Web inspired palette
        'mono': {
          // Light mode colors
          'text': '#000000',        // Pure black text
          'text-alt': '#666666',    // Alternative gray text
          'bg': '#ffffff',          // Pure white background
          'bg-alt': '#eeeeee',      // Alternative light gray background
          'border': '#000000',      // Black borders
          
          // Dark mode colors (CSS variables will handle the switch)
          'text-dark': '#ffffff',
          'text-alt-dark': '#aaaaaa', 
          'bg-dark': '#000000',
          'bg-alt-dark': '#111111',
          'border-dark': '#ffffff',
          
          // Traditional gray scale for compatibility
          50: '#ffffff',
          100: '#eeeeee',
          200: '#cccccc',
          300: '#aaaaaa',
          400: '#888888',
          500: '#666666',
          600: '#444444',
          700: '#333333',
          800: '#111111',
          900: '#000000',
        },
        // Minimal accent colors
        'accent': {
          50: '#f0f0f0',
          100: '#e0e0e0',
          500: '#333333',
          600: '#222222',
          700: '#111111'
        },
        // Status colors (subtle, monospace-friendly)
        'success': {
          50: '#f0f0f0',
          100: '#e0e0e0',
          500: '#666666',
          600: '#555555',
          700: '#444444'
        },
        'warning': {
          50: '#f0f0f0',
          100: '#e0e0e0',
          500: '#666666',
          600: '#555555',
          700: '#444444'
        },
        'error': {
          50: '#f0f0f0',
          100: '#e0e0e0',
          500: '#666666',
          600: '#555555',
          700: '#444444'
        }
      },
      spacing: {
        // Character-based spacing (ch units)
        'ch': '1ch',
        '2ch': '2ch',
        '3ch': '3ch',
        '4ch': '4ch',
        '6ch': '6ch',
        '8ch': '8ch',
        '12ch': '12ch',
        '16ch': '16ch',
        '20ch': '20ch',
        '24ch': '24ch',
        '32ch': '32ch',
        '40ch': '40ch',
        '48ch': '48ch',
        '60ch': '60ch',
        '80ch': '80ch',
        
        // Line-height based vertical spacing
        'line': '1.2rem',
        '2line': '2.4rem',
        '3line': '3.6rem',
        '4line': '4.8rem',
        
        // Traditional spacing (keep some for compatibility)
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem'
      },
      lineHeight: {
        'mono': '1.2rem',
        'mono-tight': '1.2rem',
        'mono-relaxed': '1.4rem'
      },
      fontSize: {
        'mono-xs': ['0.75rem', '1.2rem'],
        'mono-sm': ['0.875rem', '1.2rem'], 
        'mono-base': ['1rem', '1.2rem'],
        'mono-lg': ['1.125rem', '1.2rem'],
        'mono-xl': ['1.25rem', '1.2rem'],
        'mono-2xl': ['2rem', '2.4rem'],
      },
      typography: {
        DEFAULT: {
          css: {
            fontFamily: 'JetBrains Mono, SF Mono, Monaco, Menlo, Consolas, Liberation Mono, Courier New, monospace',
            fontSize: '1rem',
            lineHeight: '1.2rem',
            fontWeight: '500',
            'code::before': {
              content: '""'
            },
            'code::after': {
              content: '""'
            },
            'h1': {
              fontSize: '2rem',
              lineHeight: '2.4rem',
              fontWeight: '800',
              textTransform: 'uppercase',
              marginTop: '2.4rem',
              marginBottom: '2.4rem'
            },
            'h2': {
              fontSize: '1rem',
              lineHeight: '1.2rem', 
              fontWeight: '800',
              textTransform: 'uppercase',
              marginTop: '2.4rem',
              marginBottom: '1.2rem'
            },
            'h3, h4, h5, h6': {
              fontSize: '1rem',
              lineHeight: '1.2rem',
              fontWeight: '600',
              marginTop: '2.4rem',
              marginBottom: '1.2rem'
            },
            'p': {
              marginBottom: '1.2rem'
            },
            'strong': {
              fontWeight: '800'
            },
            'code': {
              fontWeight: '600'
            }
          }
        }
      },
      textTransform: {
        'mono-upper': 'uppercase',
        'mono-lower': 'lowercase', 
        'mono-capital': 'capitalize'
      },
      borderWidth: {
        'mono': '2px',
        'mono-thick': '3px',
        'mono-thin': '1px',
        '1': '1px',
        '2': '2px', 
        '3': '3px'
      },
      borderRadius: {
        'mono': '0',
        'mono-sm': '2px'
      },
      boxShadow: {
        'mono': 'none',
        'mono-focus': '0 0 0 3px rgba(0, 0, 0, 0.1)'
      }
    },
  },
  plugins: [],
}