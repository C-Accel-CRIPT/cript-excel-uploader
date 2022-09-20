// screens
let startScreen = document.getElementById("start-screen");
let loadingScreen = document.getElementById("loading-screen");
let errorScreen = document.getElementById("error-screen");
let successScreen = document.getElementById("success-screen");


// navigate to start screen
eel.expose(goToStartScreen);
const start_URL = "start_screen.html";

function goToStartScreen() {
    // show #start-screen
    startScreen.classList.remove("hidden");

    // hide all other screens
    loadingScreen.classList.add("hidden");
    errorScreen.classList.add("hidden");
    successScreen.classList.add("hidden");
}


// navigate to loading screen
eel.expose(goToLoadingScreen);

function goToLoadingScreen() {
    // show #loading-screen
    loadingScreen.classList.remove("hidden");

    // hide all other screens
    startScreen.classList.add("hidden");
    errorScreen.classList.add("hidden");
    successScreen.classList.add("hidden");
}

// navigate to error screen
eel.expose(goToErrorScreen);

function goToErrorScreen() {
        // show #error-screen
    errorScreen.classList.remove("hidden");

    // hide all other screens
    loadingScreen.classList.add("hidden");
    startScreen.classList.add("hidden");
    successScreen.classList.add("hidden");
}

// navigate to Success screen
eel.expose(goToSuccessScreen);

function goToSuccessScreen() {
        // show #success-screen
    successScreen.classList.remove("hidden");

    // hide all other screens
    loadingScreen.classList.add("hidden");
    errorScreen.classList.add("hidden");
    startScreen.classList.add("hidden");
}
