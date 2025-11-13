/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html",
        "./apps/**/templates/**/*.html",
        "./static/js/**/*.js",
    ],
    theme: {
        extend: {
            colors: {
                "sitera-primary": "#047857",
                "sitera-secondary": "#065F46",
                "sitera-dark": "#064E3B",
                "sitera-light": "#F0FDF4",
                "sitera-gray": "#495057",
                "sitera-border": "#D1FAE5",
                "sitera-hover": "#ECFDF5",
            },
            fontFamily: {
                inter: ["Inter", "sans-serif"],
            },
            fontSize: {
                h1: ["48px", { lineHeight: "1.2", letterSpacing: "-0.02em" }],
                h2: ["32px", { lineHeight: "1.3", letterSpacing: "-0.01em" }],
                body: ["18px", { lineHeight: "1.6" }],
                "body-sm": ["16px", { lineHeight: "1.6" }],
            },
            screens: {
                mobile: { max: "767px" },
                desktop: { min: "768px" },
            },
            gridTemplateColumns: {
                6: "repeat(6, minmax(0, 1fr))",
            },
        },
    },
    plugins: [
        require("@tailwindcss/forms"),
        require("@tailwindcss/typography"),
    ],
};
