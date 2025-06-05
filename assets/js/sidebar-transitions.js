// Check if admin view is loaded
function isAdminView() {
    return document.getElementById('sidebar-column') !== null && 
           document.getElementById('sidebar-toggle') !== null;
}

document.addEventListener('DOMContentLoaded', function () {
    if (!isAdminView()) {
        console.log("No Admin View. Skipping init...");
        return;
    }

    // Get DOM elements
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarColumn = document.getElementById('sidebar-column');
    const mainContent = document.getElementById('main-content-column');
    const toggleContainer = document.getElementById('sidebar-toggle-container');

    // Function to check if we're on mobile
    function isMobile() {
        return window.innerWidth < 768;
    }

    // Initialize sidebar state
    function initSidebar() {
        if (isMobile()) {
            const isCollapsed = sidebarColumn == null ? false : sidebarColumn.classList.contains('sidebar-collapsed');

            // On mobile, sidebar starts closed
            if (!isCollapsed) {
                sidebarColumn.classList.add('sidebar-collapsed');
            }
            sidebarToggle.textContent = '❯'; // Right arrow icon

            // Position toggle container
            if (toggleContainer) {
                toggleContainer.style.left = '0';
            }
        } else {
            // On desktop, check current state
            const isCollapsed = sidebarColumn == null ? false : sidebarColumn.classList.contains('sidebar-collapsed');

            // Update toggle button text
            if (isCollapsed) {
                sidebarToggle.textContent = '❯'; // Right arrow when collapsed
                if (toggleContainer) {
                    toggleContainer.style.left = '0';
                }
            } else {
                sidebarToggle.textContent = '❮'; // Left arrow when expanded
                if (toggleContainer) {
                    toggleContainer.style.left = '300px'; // Match sidebar width
                }
            }
        }
    }

    // Handle window resize
    window.addEventListener('resize', function () {
        initSidebar();
    });

    // Initial setup - only handle initialization, let callback handle toggle
    initSidebar();
});