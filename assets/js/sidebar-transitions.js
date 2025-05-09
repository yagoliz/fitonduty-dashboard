// Fixed sidebar transitions JavaScript compatible with callback
document.addEventListener('DOMContentLoaded', function() {
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
          // On mobile, sidebar starts closed
          if (!sidebarColumn.classList.contains('sidebar-collapsed')) {
              sidebarColumn.classList.add('sidebar-collapsed');
          }
          sidebarToggle.textContent = '❯'; // Right arrow icon
          
          // Position toggle container
          if (toggleContainer) {
              toggleContainer.style.left = '0';
          }
      } else {
          // On desktop, check current state
          const isCollapsed = sidebarColumn.classList.contains('sidebar-collapsed');
          
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
  window.addEventListener('resize', function() {
      initSidebar();
  });
  
  // Initial setup - only handle initialization, let callback handle toggle
  initSidebar();
});