document.addEventListener('DOMContentLoaded', function () {
    const authBox = document.getElementById('authBox');
    const toggleBtn = document.getElementById('auth-toggle-btn');

    if (!authBox) {
        console.warn('Auth box container not found. Skipping auth toggle setup.');
        return;
    }

    if (!toggleBtn) {
        console.warn('Toggle button not found. Skipping auth toggle setup.');
        return;
    }

    const targetUrl = toggleBtn.getAttribute('data-target-url');

    if (!targetUrl) {
        console.error('Toggle button is missing data-target-url attribute.');
        return;
    }

    // Add smooth flip animation before redirect
    toggleBtn.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent default in case of <a> misuse

        // Add flipping class for animation
        authBox.classList.add('flipping');

        // Optional: Add a subtle delay to let animation play
        setTimeout(() => {
            window.location.href = targetUrl;
        }, 400); // Matches CSS transition duration
    });

    // Optional: Allow pressing Enter on focused button
    toggleBtn.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleBtn.click();
        }
    });
});