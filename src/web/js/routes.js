// TODO could use some refactoring to get it a lot cleaner and simpler

// base url of the app
const rootUrl = "http://localhost:8000/templates"


// navigate to start screen
eel.expose(goToStartScreen);
const start_URL = "start_screen.html";

function goToStartScreen() {
    window.location.replace(`${rootUrl}/${start_URL}`);
}


// navigate to loading screen
eel.expose(goToLoadingScreen);

function goToLoadingScreen() {
    const loading_URL = "loading_screen.html";
    window.location.replace(`${rootUrl}/${loading_URL}`);
}

// navigate to error screen
eel.expose(goToErrorScreen);

function goToErrorScreen() {
    const error_URL = "error_screen.html";
    window.location.replace(`${rootUrl}/${error_URL}`);
}

// navigate to Success screen
eel.expose(goToSuccessScreen);

function goToSuccessScreen() {
    const success_URL = "success_screen.html";
    window.location.replace(`${rootUrl}/${success_URL}`);
}
