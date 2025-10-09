/**
 * Navbar Active State Manager
 * Manages the active state of navigation links in offcanvas
 */

class NavbarManager {
    constructor() {
        // Map routes to their corresponding navigation link IDs
        this.routeToIdMap = {
            '/': 'home-link',
            '/home': 'home-link',
            '/settings': 'settings-link',
            // Add more mappings as you implement the routes
            '/staff': 'staff-link',
            '/schedule': 'schedule-link',
            '/layouts': 'layouts-link',
            '/tasks': 'tasks-link',
            '/invox': 'invox-link'
        };

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

        // Get the corresponding link ID for the current path
        const activeLinkId = this.routeToIdMap[currentPath];

        if (activeLinkId) {
            this.setActiveLinkById(activeLinkId);
        } else {
            // Fallback: try to find a link by href if no ID mapping exists
            this.setActiveLinkByHref(currentPath);
        }
    }

    /**
     * Set a specific link as active by ID
     * @param {string} linkId - The ID of the link element to set as active
     */
    setActiveLinkById(linkId) {
        // Remove active class from all navigation links
        this.clearAllActiveStates();

        // Find and activate the specific link by ID
        const activeLink = document.getElementById(linkId);
        if (activeLink && activeLink.classList.contains('nav-link')) {
            activeLink.classList.add('active');
            activeLink.setAttribute('aria-current', 'page');
        }
    }

    /**
     * Set a specific link as active by href (fallback method)
     * @param {string} href - The href to match
     */
    setActiveLinkByHref(href) {
        const navLinks = document.querySelectorAll('.offcanvas .nav-pills .nav-link');

        navLinks.forEach(link => {
            const linkPath = new URL(link.href).pathname;
            if (linkPath === href) {
                this.setActiveLink(link);
            }
        });
    }

    /**
     * Clear active state from all navigation links
     */
    clearAllActiveStates() {
        document.querySelectorAll('.offcanvas .nav-pills .nav-link').forEach(link => {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
        });
    }



    /**
     * Attach click handlers to navigation links
     */
    attachClickHandlers() {
        const navLinks = document.querySelectorAll('.offcanvas .nav-pills .nav-link');

        navLinks.forEach(link => {
            // Skip logout link as it doesn't need active state
            if (link.getAttribute('href') === '/logout') {
                return;
            }

            link.addEventListener('click', (e) => {
                const linkId = link.id;

                if (linkId) {
                    // Set active state using ID
                    this.setActiveLinkById(linkId);
                } else {
                    // If no ID is present, we can't set active state properly
                    console.warn('Navigation link missing ID:', link.href);
                }

                // Close offcanvas after clicking a link
                const offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('offcanvasNavbar'));
                if (offcanvas) {
                    offcanvas.hide();
                }
            });
        });
    }


}

// Initialize navbar manager when DOM is loaded
let navbarManager;
document.addEventListener('DOMContentLoaded', () => {
    navbarManager = new NavbarManager();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    if (navbarManager) {
        navbarManager.setActiveLinkFromURL();
    }
});