// assets/js/responsive-charts.js
window.addEventListener('load', function() {
    // Initial setup
    setupResponsiveCharts();
    
    // Watch for sidebar toggle events
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            // Wait for transition to complete
            setTimeout(resizeAllCharts, 350);
        });
    }
    
    // Watch for window resize events
    window.addEventListener('resize', function() {
        // Debounce to avoid too many redraws
        if (window.resizeTimeout) {
            clearTimeout(window.resizeTimeout);
        }
        window.resizeTimeout = setTimeout(resizeAllCharts, 250);
    });
});

function setupResponsiveCharts() {
    // Create MutationObserver to detect when new charts are added to the DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                // Check if any of the added nodes are or contain chart containers
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.querySelectorAll) {
                        const charts = node.querySelectorAll('.js-plotly-plot');
                        if (charts.length > 0) {
                            // If charts were added, resize them
                            setTimeout(resizeAllCharts, 100);
                        }
                    }
                }
            }
        });
    });

    // Start observing the document with the configured parameters
    observer.observe(document.body, { childList: true, subtree: true });
}

function resizeAllCharts() {
    const charts = document.querySelectorAll('.js-plotly-plot');
    charts.forEach(function(chart) {
        if (chart && chart.on) {
            try {
                Plotly.Plots.resize(chart);
            } catch (e) {
                console.error('Error resizing chart:', e);
            }
        }
    });
}