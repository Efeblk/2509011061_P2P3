/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                bg: {
                    main: "#1e1e2e",
                    card: "#2b2b40",
                },
                accent: {
                    cyan: "#00d2ff",
                    blue: "#3a7bd5",
                    orange: "#ff9f43",
                    purple: "#a55eea",
                    green: "#43e97b",
                    red: "#ff6b6b",
                }
            },
            animation: {
                'gradient': 'gradient 15s ease infinite',
            },
            keyframes: {
                gradient: {
                    '0%, 100%': { backgroundPosition: '0% 50%' },
                    '50%': { backgroundPosition: '100% 50%' },
                }
            }
        },
    },
    plugins: [],
    important: true,
}
