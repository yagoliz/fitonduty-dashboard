// assets/sidebar-transitions.js
document.addEventListener('DOMContentLoaded', function() {
    // Prevent content flashing during sidebar transitions
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarColumn = document.getElementById('sidebar-column');
    const mainContent = document.getElementById('main-content-column');
    
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', function() {
        // Add a class to the body to indicate transition is happening
        document.body.classList.add('sidebar-transitioning');
        
        // After transition completes, remove the class
        setTimeout(function() {
          document.body.classList.remove('sidebar-transitioning');
        }, 300); // Match this with your CSS transition time
      });
    }
    
    // Ensure content height is maintained during transitions
    function updateContentHeight() {
      const mainContentInner = document.querySelector('.main-content-inner');
      if (mainContentInner) {
        // Get the current height before transition
        const currentHeight = mainContentInner.offsetHeight;
        
        // Set a minimum height during transitions
        mainContentInner.style.minHeight = currentHeight + 'px';
        
        // Remove fixed height after transition
        setTimeout(function() {
          mainContentInner.style.minHeight = '';
        }, 350);
      }
    }
    
    // Call when sidebar toggle is clicked
    if (sidebarToggle) {
      sidebarToggle.addEventListener('click', updateContentHeight);
    }
    
    // Call on window resize to handle responsive changes
    window.addEventListener('resize', function() {
      if (document.body.classList.contains('sidebar-transitioning')) {
        return; // Skip during transitions
      }
      updateContentHeight();
    });
  });