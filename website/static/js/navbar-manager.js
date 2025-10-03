/**
 * Navbar Active State Manager
 * Manages the active state of navigation links in offcanvas
 */

class NavbarManager {
    constructor() {
        this.init();
    }

    init() {
        // Set active link based on current URL when page loads
        this.setActiveLinkFromURL();

        // Add click handlers to navigation links
        this.attachClickHandlers();
    }

    /**
     * Set the active link based on the current URL
     */
    setActiveLinkFromURL() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.offcanvas .nav-pills .nav-link');

        navLinks.forEach(link => {
            link.classList.remove('active');
            link.removeAttribute('aria-current');

            // Check if the link's href matches the current path
            const linkPath = new URL(link.href).pathname;
            if (linkPath === currentPath) {
                this.setActiveLink(link);
            }
        });

        // Special case for home page - if no match found and we're at root
        if (currentPath === '/' || currentPath === '') {
            const homeLink = document.querySelector('.offcanvas .nav-pills .nav-link[href="/"]');
            if (homeLink && !document.querySelector('.offcanvas .nav-pills .nav-link.active')) {
                this.setActiveLink(homeLink);
            }
        }
    }

    /**
     * Set a specific link as active
     * @param {HTMLElement} activeLink - The link element to set as active
     */
    setActiveLink(activeLink) {
        // Remove active class from all navigation links in offcanvas
        document.querySelectorAll('.offcanvas .nav-pills .nav-link').forEach(link => {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
        });

        // Add active class to the clicked link
        activeLink.classList.add('active');
        activeLink.setAttribute('aria-current', 'page');
    }

    /**
     * Attach click handlers to navigation links
     */
    attachClickHandlers() {
        const navLinks = document.querySelectorAll('.offcanvas .nav-pills .nav-link');

        navLinks.forEach(link => {
            // Skip logout link as it doesn't need active state (it's not in offcanvas anymore)
            if (link.getAttribute('href') === '/logout') {
                return;
            }

            link.addEventListener('click', (e) => {
                // Set active state immediately for better UX
                this.setActiveLink(link);

                // Store the active link in sessionStorage for persistence
                sessionStorage.setItem('activeNavLink', link.getAttribute('href'));

                // Close offcanvas after clicking a link (optional)
                const offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('navigationOffcanvas'));
                if (offcanvas) {
                    offcanvas.hide();
                }
            });
        });
    }

    /**
     * Restore active state from sessionStorage if available
     */
    restoreActiveState() {
        const storedActiveLink = sessionStorage.getItem('activeNavLink');
        if (storedActiveLink) {
            const link = document.querySelector(`.offcanvas .nav-pills .nav-link[href="${storedActiveLink}"]`);
            if (link) {
                this.setActiveLink(link);
            }
        }
    }
}

// Initialize navbar manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NavbarManager();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    const navbarManager = new NavbarManager();
    navbarManager.setActiveLinkFromURL();
});