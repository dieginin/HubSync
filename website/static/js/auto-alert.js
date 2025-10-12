// Auto-dismiss alerts after 7.5 seconds (only if they have a close button)
setTimeout(() => {
    const alertList = document.querySelectorAll('.alert');
    alertList.forEach((alert) => {
        // Only close alerts that have a close button
        const closeButton = alert.querySelector('.btn-close');
        if (closeButton) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    });
}, 7500);