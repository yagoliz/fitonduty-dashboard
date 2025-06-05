// Robust admin charts resize handling - continuous monitoring
(function() {
    let isMonitoring = false;
    let monitoringInterval = null;
    
    function resizeAllAdminCharts() {
        const adminCharts = document.querySelectorAll('#admin-data-visualizations .js-plotly-plot');
        
        if (adminCharts.length > 0) {
            console.log('Resizing admin charts:', adminCharts.length);
            
            adminCharts.forEach(function(chart, index) {
                if (chart && window.Plotly) {
                    try {
                        window.Plotly.Plots.resize(chart);
                        console.log(`Resized chart ${index}`);
                    } catch (e) {
                        console.error('Error resizing admin chart:', e);
                    }
                }
            });
        }
    }
    
    function handleSidebarToggle() {
        console.log('Sidebar toggle detected, scheduling chart resize');
        setTimeout(resizeAllAdminCharts, 350);
    }
    
    function startMonitoring() {
        if (isMonitoring) return;
        
        console.log('Starting admin chart monitoring');
        isMonitoring = true;
        
        // Monitor every 500ms for sidebar toggle and admin charts
        monitoringInterval = setInterval(function() {
            const sidebarToggle = document.getElementById('sidebar-toggle');
            const adminViz = document.getElementById('admin-data-visualizations');
            
            // If we find the sidebar toggle button, attach listener if not already attached
            if (sidebarToggle && !sidebarToggle.hasAttribute('data-chart-listener')) {
                console.log('Found sidebar toggle, attaching listener');
                sidebarToggle.setAttribute('data-chart-listener', 'true');
                sidebarToggle.addEventListener('click', handleSidebarToggle);
            }
            
            // If admin visualizations disappear (logout), stop monitoring
            if (!adminViz && isMonitoring) {
                console.log('Admin visualizations gone, stopping monitoring');
                stopMonitoring();
            }
        }, 500);
        
        // Also add window resize listener
        window.addEventListener('resize', function() {
            if (window.adminResizeTimeout) {
                clearTimeout(window.adminResizeTimeout);
            }
            window.adminResizeTimeout = setTimeout(resizeAllAdminCharts, 250);
        });
    }
    
    function stopMonitoring() {
        if (!isMonitoring) return;
        
        console.log('Stopping admin chart monitoring');
        isMonitoring = false;
        
        if (monitoringInterval) {
            clearInterval(monitoringInterval);
            monitoringInterval = null;
        }
        
        // Clean up any existing listeners
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle && sidebarToggle.hasAttribute('data-chart-listener')) {
            sidebarToggle.removeAttribute('data-chart-listener');
            sidebarToggle.removeEventListener('click', handleSidebarToggle);
        }
        
        if (window.adminResizeTimeout) {
            clearTimeout(window.adminResizeTimeout);
            window.adminResizeTimeout = null;
        }
    }
    
    // Start monitoring when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            // Wait a bit for Dash to finish initial rendering
            setTimeout(function() {
                if (document.getElementById('admin-data-visualizations')) {
                    startMonitoring();
                }
            }, 1000);
        });
    } else {
        // DOM is already ready
        setTimeout(function() {
            if (document.getElementById('admin-data-visualizations')) {
                startMonitoring();
            }
        }, 1000);
    }
    
    // Also monitor for admin visualizations appearing (for login scenarios)
    const globalObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.id === 'admin-data-visualizations' || 
                        (node.querySelector && node.querySelector('#admin-data-visualizations'))) {
                        console.log('Admin visualizations appeared, starting monitoring');
                        setTimeout(startMonitoring, 500);
                        return;
                    }
                }
            }
        });
    });
    
    globalObserver.observe(document.body, { 
        childList: true, 
        subtree: true 
    });
    
    // Export for manual calls
    window.resizeAdminCharts = resizeAllAdminCharts;
    window.startAdminChartMonitoring = startMonitoring;
    window.stopAdminChartMonitoring = stopMonitoring;
})();