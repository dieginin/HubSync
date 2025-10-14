/**
 * Pull to Refresh functionality for HubSync
 * Implements a mobile-friendly pull-to-refresh gesture
 */

class PullToRefresh {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            threshold: 110, // Distance to trigger refresh
            resistance: 2.5, // Resistance while pulling
            refreshCallback: () => window.location.reload(),
            onPull: null,
            onRelease: null,
            ...options
        };

        this.isEnabled = true;
        this.isRefreshing = false;
        this.startY = 0;
        this.currentY = 0;
        this.pullDistance = 0;
        this.isAtTop = false;

        this.init();
    }

    init() {
        this.createElements();
        this.bindEvents();
    }

    /**
     * Check if there's an active modal (Bootstrap modal detection)
     * @returns {boolean} True if a modal is currently open
     */
    isModalOpen() {
        // Check for Bootstrap modals that are currently shown
        const activeModal = document.querySelector('.modal.show');

        // Also check for any element with modal-open class on body (Bootstrap adds this)
        const bodyHasModalOpen = document.body.classList.contains('modal-open');

        // Check for any backdrop (Bootstrap modal backdrop)
        const hasModalBackdrop = document.querySelector('.modal-backdrop');

        return activeModal || bodyHasModalOpen || hasModalBackdrop;
    }

    createElements() {
        // Check if elements already exist to prevent duplication
        if (this.container.querySelector('.pull-to-refresh-indicator') ||
            this.container.querySelector('.pull-to-refresh-message') ||
            this.container.querySelector('.pull-to-refresh-content')) {
            // Elements already exist, just get references to them
            this.indicator = this.container.querySelector('.pull-to-refresh-indicator');
            this.message = this.container.querySelector('.pull-to-refresh-message');
            this.content = this.container.querySelector('.pull-to-refresh-content');
            return;
        }

        // Create pull indicator
        this.indicator = document.createElement('div');
        this.indicator.className = 'pull-to-refresh-indicator';
        this.indicator.innerHTML = '<i class="bi bi-arrow-down"></i>';

        // Create message element
        this.message = document.createElement('div');
        this.message.className = 'pull-to-refresh-message';
        this.message.textContent = 'Pull down to refresh';

        // Create content wrapper
        this.content = document.createElement('div');
        this.content.className = 'pull-to-refresh-content';

        // Wrap existing content
        while (this.container.firstChild) {
            this.content.appendChild(this.container.firstChild);
        }

        // Add elements to container
        this.container.classList.add('pull-to-refresh-container');
        this.container.appendChild(this.indicator);
        this.container.appendChild(this.message);
        this.container.appendChild(this.content);
    }

    bindEvents() {
        // Store bound methods to enable proper cleanup
        this.boundHandlers = {
            touchStart: this.handleTouchStart.bind(this),
            touchMove: this.handleTouchMove.bind(this),
            touchEnd: this.handleTouchEnd.bind(this),
            mouseDown: this.handleMouseDown.bind(this),
            mouseMove: this.handleMouseMove.bind(this),
            mouseEnd: this.handleMouseEnd.bind(this),
            scroll: this.handleScroll.bind(this)
        };

        // Use document-wide events for better coverage when content is small
        // Touch events for mobile
        document.addEventListener('touchstart', this.boundHandlers.touchStart, { passive: false });
        document.addEventListener('touchmove', this.boundHandlers.touchMove, { passive: false });
        document.addEventListener('touchend', this.boundHandlers.touchEnd, { passive: false });

        // Mouse events for desktop testing
        document.addEventListener('mousedown', this.boundHandlers.mouseDown);
        document.addEventListener('mousemove', this.boundHandlers.mouseMove);
        document.addEventListener('mouseup', this.boundHandlers.mouseEnd);

        // Monitor scroll for the entire window to detect top position
        window.addEventListener('scroll', this.boundHandlers.scroll);
        this.container.addEventListener('scroll', this.boundHandlers.scroll);
    }

    handleTouchStart(e) {
        if (!this.isEnabled || this.isRefreshing) return;

        // Check if there's an active modal (Bootstrap modal detection)
        if (this.isModalOpen()) return;

        // Check if we're at the top of the page
        this.isAtTop = (window.scrollY === 0 || document.documentElement.scrollTop === 0) &&
            this.container.scrollTop === 0;

        if (this.isAtTop) {
            this.startY = e.touches[0].clientY;
            this.isPulling = false;
        }
    }

    handleTouchMove(e) {
        if (!this.isEnabled || this.isRefreshing) return;

        // Check if there's an active modal (Bootstrap modal detection)
        if (this.isModalOpen()) return;

        // Check if we're still at the top
        const isCurrentlyAtTop = (window.scrollY === 0 || document.documentElement.scrollTop === 0) &&
            this.container.scrollTop === 0;

        if (!isCurrentlyAtTop && !this.isPulling) return;

        this.currentY = e.touches[0].clientY;
        const deltaY = this.currentY - this.startY;

        if (deltaY > 0 && isCurrentlyAtTop) {
            e.preventDefault();
            this.isPulling = true;
            this.pullDistance = deltaY / this.options.resistance;
            this.updateUI();

            if (this.options.onPull) {
                this.options.onPull(this.pullDistance);
            }
        }
    }

    handleTouchEnd(e) {
        if (!this.isEnabled || this.isRefreshing) return;

        if (this.isPulling) {
            if (this.pullDistance >= this.options.threshold) {
                this.triggerRefresh();
            } else {
                this.resetPull();
            }

            if (this.options.onRelease) {
                this.options.onRelease(this.pullDistance);
            }
        }

        this.isPulling = false;
    }

    // Mouse events for desktop testing
    handleMouseDown(e) {
        if (!this.isEnabled || this.isRefreshing) return;

        // Check if there's an active modal (Bootstrap modal detection)
        if (this.isModalOpen()) return;

        // Check if we're at the top of the page
        this.isAtTop = (window.scrollY === 0 || document.documentElement.scrollTop === 0) &&
            this.container.scrollTop === 0;

        if (this.isAtTop) {
            this.startY = e.clientY;
            this.isDragging = true;
            this.isPulling = false;
        }
    }

    handleMouseMove(e) {
        if (!this.isEnabled || this.isRefreshing || !this.isDragging) return;

        // Check if there's an active modal (Bootstrap modal detection)
        if (this.isModalOpen()) return;

        // Check if we're still at the top
        const isCurrentlyAtTop = (window.scrollY === 0 || document.documentElement.scrollTop === 0) &&
            this.container.scrollTop === 0;

        if (!isCurrentlyAtTop && !this.isPulling) return;

        this.currentY = e.clientY;
        const deltaY = this.currentY - this.startY;

        if (deltaY > 0 && isCurrentlyAtTop) {
            e.preventDefault();
            this.isPulling = true;
            this.pullDistance = deltaY / this.options.resistance;
            this.updateUI();

            if (this.options.onPull) {
                this.options.onPull(this.pullDistance);
            }
        }
    }

    handleMouseEnd(e) {
        if (!this.isEnabled || this.isRefreshing || !this.isDragging) return;

        this.isDragging = false;

        if (this.isPulling) {
            if (this.pullDistance >= this.options.threshold) {
                this.triggerRefresh();
            } else {
                this.resetPull();
            }

            if (this.options.onRelease) {
                this.options.onRelease(this.pullDistance);
            }
        }

        this.isPulling = false;
    }

    handleScroll() {
        this.isAtTop = (window.scrollY === 0 || document.documentElement.scrollTop === 0) &&
            this.container.scrollTop === 0;

        // Reset pull if we're no longer at the top and not actively pulling
        if (!this.isAtTop && !this.isPulling && this.pullDistance > 0) {
            this.resetPull();
        }
    }

    updateUI() {
        // Ensure elements exist before updating them
        this.ensureElementsExist();

        const progress = Math.min(this.pullDistance / this.options.threshold, 1);

        // Update indicator visibility and position
        if (this.pullDistance > 10) {
            if (this.indicator) this.indicator.classList.add('visible');
            if (this.message) this.message.classList.add('visible');
        } else {
            if (this.indicator) this.indicator.classList.remove('visible');
            if (this.message) this.message.classList.remove('visible');
        }

        // Update content position
        if (this.content) {
            this.content.style.transform = `translateY(${Math.min(this.pullDistance, this.options.threshold)}px)`;
        }

        // Update indicator state
        if (this.pullDistance >= this.options.threshold) {
            if (this.indicator) this.indicator.classList.add('ready');
            if (this.message) this.message.textContent = 'Release to refresh';
        } else {
            if (this.indicator) this.indicator.classList.remove('ready');
            if (this.message) this.message.textContent = 'Pull down to refresh';
        }

        // Rotate arrow based on progress
        if (this.indicator) {
            const rotation = progress * 180;
            const arrow = this.indicator.querySelector('i');
            if (arrow) {
                arrow.style.transform = `rotate(${rotation}deg)`;
            }
        }
    }

    triggerRefresh() {
        if (this.isRefreshing) return;

        this.isRefreshing = true;
        this.indicator.classList.add('loading');
        this.indicator.classList.remove('ready');
        this.message.textContent = 'Refreshing...';

        // Change arrow to loading spinner
        const arrow = this.indicator.querySelector('i');
        if (arrow) {
            arrow.className = 'bi bi-arrow-clockwise';
            arrow.style.transform = 'none';
        }

        // Keep content in pulled position during refresh
        this.content.style.transform = `translateY(${this.options.threshold}px)`;

        // Execute refresh callback with a minimum delay to show the spinner
        setTimeout(() => {
            Promise.resolve(this.options.refreshCallback()).finally(() => {
                setTimeout(() => {
                    this.resetPull();
                    this.isRefreshing = false;
                    // Re-create elements if they were destroyed during refresh
                    this.ensureElementsExist();
                }, 200); // Brief delay after callback completes
            });
        }, 800); // Minimum delay to show the spinner
    }

    ensureElementsExist() {
        // Get current elements in the container
        const existingIndicator = this.container.querySelector('.pull-to-refresh-indicator');
        const existingMessage = this.container.querySelector('.pull-to-refresh-message');
        const existingContent = this.container.querySelector('.pull-to-refresh-content');

        // Update our references to existing elements if they exist
        if (existingIndicator) this.indicator = existingIndicator;
        if (existingMessage) this.message = existingMessage;
        if (existingContent) this.content = existingContent;

        // Only create missing elements, not all of them
        if (!existingIndicator) {
            this.indicator = document.createElement('div');
            this.indicator.className = 'pull-to-refresh-indicator';
            this.indicator.innerHTML = '<i class="bi bi-arrow-down"></i>';
            this.container.insertBefore(this.indicator, this.container.firstChild);
        }

        if (!existingMessage) {
            this.message = document.createElement('div');
            this.message.className = 'pull-to-refresh-message';
            this.message.textContent = 'Pull down to refresh';
            this.container.insertBefore(this.message, this.content || this.container.firstChild);
        }

        if (!existingContent) {
            this.content = document.createElement('div');
            this.content.className = 'pull-to-refresh-content';

            // Move non-pull-to-refresh elements into content div
            const childrenToMove = [];
            for (let child of this.container.children) {
                if (!child.classList.contains('pull-to-refresh-indicator') &&
                    !child.classList.contains('pull-to-refresh-message') &&
                    !child.classList.contains('pull-to-refresh-content')) {
                    childrenToMove.push(child);
                }
            }

            childrenToMove.forEach(child => this.content.appendChild(child));
            this.container.appendChild(this.content);
        }

        // Ensure container has the proper class
        this.container.classList.add('pull-to-refresh-container');
    }

    resetPull() {
        this.pullDistance = 0;

        // Ensure elements exist before manipulating them
        this.ensureElementsExist();

        if (this.content) {
            this.content.style.transform = 'translateY(0)';
        }

        if (this.indicator) {
            this.indicator.classList.remove('visible', 'ready', 'loading');
        }

        if (this.message) {
            this.message.classList.remove('visible');
        }

        // Reset arrow
        if (this.indicator) {
            const arrow = this.indicator.querySelector('i');
            if (arrow) {
                arrow.className = 'bi bi-arrow-down';
                arrow.style.transform = 'none';
            }
        }
    }

    enable() {
        this.isEnabled = true;
    }

    disable() {
        this.isEnabled = false;
        this.resetPull();
    }

    destroy() {
        // Remove event listeners from document using stored bound handlers
        if (this.boundHandlers) {
            document.removeEventListener('touchstart', this.boundHandlers.touchStart);
            document.removeEventListener('touchmove', this.boundHandlers.touchMove);
            document.removeEventListener('touchend', this.boundHandlers.touchEnd);
            document.removeEventListener('mousedown', this.boundHandlers.mouseDown);
            document.removeEventListener('mousemove', this.boundHandlers.mouseMove);
            document.removeEventListener('mouseup', this.boundHandlers.mouseEnd);
            window.removeEventListener('scroll', this.boundHandlers.scroll);
            this.container.removeEventListener('scroll', this.boundHandlers.scroll);
        }

        // Remove elements
        if (this.indicator && this.indicator.parentNode) this.indicator.remove();
        if (this.message && this.message.parentNode) this.message.remove();

        // Unwrap content
        if (this.content && this.content.parentNode) {
            while (this.content.firstChild) {
                this.container.appendChild(this.content.firstChild);
            }
            this.content.remove();
        }

        this.container.classList.remove('pull-to-refresh-container');
    }
}

// Auto-initialize for pages with data-pull-to-refresh attribute
document.addEventListener('DOMContentLoaded', function () {
    const containers = document.querySelectorAll('[data-pull-to-refresh]');

    containers.forEach(container => {
        // Prevent multiple initializations
        if (container.dataset.pullToRefreshInitialized) return;
        container.dataset.pullToRefreshInitialized = 'true';

        const options = {};

        // Parse data attributes for options
        if (container.dataset.refreshUrl) {
            options.refreshCallback = () => {
                // Simple page reload - most reliable solution
                window.location.reload();
            };
        }

        if (container.dataset.threshold) {
            options.threshold = parseInt(container.dataset.threshold);
        }

        const pullToRefreshInstance = new PullToRefresh(container, options);

        // Store instance for potential cleanup
        container._pullToRefreshInstance = pullToRefreshInstance;
    });
});

// Export for manual initialization
window.PullToRefresh = PullToRefresh;