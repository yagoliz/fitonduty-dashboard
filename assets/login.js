// Initialize the clientside namespace if it doesn't exist
if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    handleEnterKey: function(n_submit) {
        // When Enter is pressed in the password field, trigger a click on the login button
        if (n_submit) {
            // Return a new value to increment n_clicks on the login button
            return 1;
        }
        return window.dash_clientside.no_update;
    }
};