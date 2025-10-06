// Auto-dismiss alerts after 7.5 seconds
setTimeout(() => {
    const alertList = document.querySelectorAll('.alert');
    alertList.forEach((alert) => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 7500);