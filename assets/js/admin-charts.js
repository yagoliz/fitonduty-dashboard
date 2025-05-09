// Special handling for admin dashboard charts
document.addEventListener('DOMContentLoaded', function() {
    // Watch for the admin data visualizations element to be added to the DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.id === 'admin-data-visualizations' || 
                        (node.querySelector && node.querySelector('#admin-data-visualizations'))) {
                        console.log('Admin visualizations loaded, setting up handlers');
                        setupAdminChartHandlers();
                        // Stop observing once we've found admin charts
                        observer.disconnect();
                    }
                }
            }
        });
    });

    // Start observing for admin charts
    observer.observe(document.body, { childList: true, subtree: true });
});

function setupAdminChartHandlers() {
    // Watch for sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            console.log('Sidebar toggle clicked, scheduling admin chart updates');
            
            // Set up a series of resizes for admin charts at different intervals
            // This ensures charts resize properly as the layout completes transitions
            const intervals = [100, 300, 500, 700, 1000];
            
            intervals.forEach(function(interval) {
                setTimeout(function() {
                    resizeAdminChartsForced();
                }, interval);
            });
        });
    }
    
    // Also resize when window is resized
    window.addEventListener('resize', function() {
        // Use debounce to avoid too many redraws
        if (window.adminResizeTimeout) {
            clearTimeout(window.adminResizeTimeout);
        }
        window.adminResizeTimeout = setTimeout(resizeAdminChartsForced, 250);
    });
}

function resizeAdminChartsForced() {
    const adminCharts = document.querySelectorAll('#admin-data-visualizations .js-plotly-plot');
    
    if (adminCharts.length > 0) {
        console.log('Force resizing admin charts:', adminCharts.length);
        
        // Process all charts
        adminCharts.forEach(function(chart) {
            if (chart && chart.on) {
                try {
                    // Force the chart to redraw at full width by first setting dimensions explicitly
                    const container = chart.closest('.chart-wrapper');
                    if (container) {
                        const width = container.clientWidth;
                        const height = container.clientHeight;
                        
                        // Set explicit dimensions
                        chart.style.width = width + 'px';
                        chart.style.height = height + 'px';
                        
                        // Force reflow
                        void chart.offsetHeight;
                        
                        // Reset to 100%
                        chart.style.width = '100%';
                        chart.style.height = '100%';
                        
                        // Resize with Plotly
                        Plotly.Plots.resize(chart);
                    } else {
                        // Fallback if no wrapper found
                        Plotly.Plots.resize(chart);
                    }
                } catch (e) {
                    console.error('Error resizing admin chart:', e);
                }
            }
        });
    }
}