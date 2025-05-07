window.addEventListener('DOMContentLoaded', function() {
    // Get screen width
    function isMobile() {
      return window.innerWidth < 768;
    }
    
    // Function to adjust sidebar based on screen size
    function adjustSidebar() {
      const sidebarToggle = document.getElementById('sidebar-toggle');
      const sidebarColumn = document.getElementById('sidebar-column');
      
      if (isMobile()) {
        // On mobile, add mobile-specific class for positioning
        sidebarColumn.classList.add('mobile-view');
        sidebarToggle.classList.add('mobile-toggle');
        
        // Check if sidebar is supposed to be open on mobile
        if (sidebarColumn.classList.contains('sidebar-mobile-open')) {
          sidebarColumn.style.transform = 'translateX(0)';
        } else {
          sidebarColumn.style.transform = 'translateX(-100%)';
        }
      } else {
        // On desktop, remove mobile-specific classes
        sidebarColumn.classList.remove('mobile-view', 'sidebar-mobile-open');
        sidebarToggle.classList.remove('mobile-toggle');
        sidebarColumn.style.transform = '';
      }
    }
    
    // Listen for toggle clicks
    document.getElementById('sidebar-toggle').addEventListener('click', function() {
      const sidebarColumn = document.getElementById('sidebar-column');
      
      if (isMobile()) {
        // On mobile, toggle the mobile open class
        sidebarColumn.classList.toggle('sidebar-mobile-open');
        if (sidebarColumn.classList.contains('sidebar-mobile-open')) {
          sidebarColumn.style.transform = 'translateX(0)';
        } else {
          sidebarColumn.style.transform = 'translateX(-100%)';
        }
      }
    });
    
    // Initial adjustment
    adjustSidebar();
    
    // Adjust on resize
    window.addEventListener('resize', adjustSidebar);
  });