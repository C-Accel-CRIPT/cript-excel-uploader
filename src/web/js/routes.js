// screens
let startScreen = document.getElementById("start-screen");
let loadingScreen = document.getElementById("loading-screen");
let globusScreen = document.getElementById("globus-auth-screen");
let errorScreen = document.getElementById("error-screen");
let successScreen = document.getElementById("success-screen");


/*
gets called by other functions to hide all screens and the function shows the screen that it needs
to be used to keep code DRY
*/
function hideAllScreens() {
    // hide all screens
    startScreen.classList.add("hidden");
    loadingScreen.classList.add("hidden");
    globusScreen.classList.add("hidden");
    errorScreen.classList.add("hidden");
    successScreen.classList.add("hidden");
}

// navigate to start screen
eel.expose(goToStartScreen);

function goToStartScreen() {
    hideAllScreens();

    // show #start-screen
    startScreen.classList.remove("hidden");
}


// navigate to loading screen
eel.expose(goToLoadingScreen);

function goToLoadingScreen() {

    hideAllScreens();

    // show #loading-screen
    loadingScreen.classList.remove("hidden");
}

eel.expose(goToGlobusAuthScreen);

function goToGlobusAuthScreen() {
    hideAllScreens();

    // remove hidden class from globus screen to show it
    globusScreen.classList.remove("hidden");
}

// navigate to error screen
eel.expose(goToErrorScreen);

function goToErrorScreen() {

    hideAllScreens();

    // show #error-screen
    errorScreen.classList.remove("hidden");
}

// navigate to Success screen
eel.expose(goToSuccessScreen);

function goToSuccessScreen() {

    hideAllScreens();

    // show #success-screen
    successScreen.classList.remove("hidden");
}
