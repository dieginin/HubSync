/**
 * HubSync Theme Manager
 * Handles automatic theme detection and manual theme switching
 */

class ThemeManager {
    constructor() {
        this.themes = {
            auto: 'auto',
            light: 'light',
            dark: 'dark'
        };

        this.currentTheme = this.getStoredTheme() || this.themes.auto;
        this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

        this.init();
    }

    init() {
        // Apply initial theme
        this.applyTheme();

        // Listen for system theme changes
        this.mediaQuery.addEventListener('change', () => {
            if (this.currentTheme === this.themes.auto) {
                this.applyTheme();
            }
        });

        // Listen for storage changes (for cross-tab synchronization with localStorage)
        window.addEventListener('storage', (e) => {
            if (e.key === 'theme_preference') {
                this.currentTheme = e.newValue || this.themes.auto;
                this.applyTheme();
            }
        });
    }

    getStoredTheme() {
        try {
            // Read from localStorage
            return localStorage.getItem('theme_preference');
        } catch {
            return null;
        }
    }

    setStoredTheme(theme) {
        try {
            if (theme === this.themes.auto) {
                // Remove from localStorage if auto
                localStorage.removeItem('theme_preference');
            } else {
                // Store in localStorage
                localStorage.setItem('theme_preference', theme);
            }
        } catch {
            // Silently handle localStorage errors
        }
    }

    getPreferredTheme() {
        if (this.currentTheme !== this.themes.auto) {
            return this.currentTheme;
        }

        return this.mediaQuery.matches ? this.themes.dark : this.themes.light;
    }

    applyTheme() {
        const theme = this.getPreferredTheme();
        const htmlElement = document.documentElement;

        // Remove all theme classes
        htmlElement.removeAttribute('data-bs-theme');

        // Apply new theme
        if (theme === this.themes.dark) {
            htmlElement.setAttribute('data-bs-theme', 'dark');
        }

        // Update meta theme-color for PWA
        this.updateMetaThemeColor(theme);

        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme: theme, mode: this.currentTheme }
        }));
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');

        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }

        // Set appropriate theme colors
        const colors = {
            light: '#248939',
            dark: '#1e2d2f'
        };

        metaThemeColor.content = colors[theme] || colors.light;
    }

    cycleTheme() {
        const themes = [this.themes.auto, this.themes.light, this.themes.dark];
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;

        this.setTheme(themes[nextIndex]);
    }

    setTheme(theme) {
        if (!Object.values(this.themes).includes(theme)) {
            return;
        }

        this.currentTheme = theme;
        this.setStoredTheme(theme);
        this.applyTheme();
    }

    // Public methods for external use
    getCurrentTheme() {
        return this.currentTheme;
    }

    getEffectiveTheme() {
        return this.getPreferredTheme();
    }

    isSystemDarkMode() {
        return this.mediaQuery.matches;
    }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Make it globally available
window.themeManager = themeManager;

// Log theme changes for debugging
window.addEventListener('themechange', (e) => {
    console.log('Theme changed:', e.detail);
});