/*
    this event is listening for the browser to be closed.
    After the user clicks to close the browser, this code runs and notifies python eel
    to exit the program
*/
addEventListener('beforeunload', (event) => {
    eel.user_closed_app()
});


/*
this function is called when the python program in the backend exits and is no longer functioning.
This function closes up the GUI so the user doesn't think the program is still running but just frozen
when python has already exited and is done
*/
eel.expose(pythonExitCleanUp);

function pythonExitCleanUp() {
    window.close()
}


/*
    this function runs when user clicks on
    "Try Again" from error screen or "Upload again" from success screen
    to try re-uploading their data
    restarts the start_screen, loading_screen, globus_screen, and error_screen
    calls the eel function to clear out the error_list so there are no old errors
    from previous upload attempt, and sets the current_progress to 0 so the progress bar
    can start from 0 and not from 100
    then takes the user to the start_screen
*/
function uploadAgain() {
    restartAllScreens();
    eel.reset_for_uploading()
    goToStartScreen();
}

/*
    restarts the start_screen, loading_screen, globus_screen, and error_screen
*/
function restartAllScreens() {

// restart start screen
    restartStartScreen();

// restart loading screen
    updateLoadingBar(0);
    // removing updating label from what the last thing it was
    document.getElementById("uploading-specifics").textContent = "...";

// restart globus screen
    // clears out the form of the token that they have already inputted and ready to accept input
    // the link for globus will get auto generated anyways
    document.getElementById("globus-auth-token-input").value = "";

// restart error screen
    // remove any errors that are already appended to the error window
document.getElementById("error-window").textContent = "";

}

/*
function used when start screen needs to be restarted to used again
it enables upload button, changes the text to upload, and
removes any feedback of valid or invalid from the screen.
However, it leaves all the original values that were inputted into the fields
*/
function restartStartScreen() {
 //    restart start screen
    // enable the start screen button
    let uploadButton = document.getElementById("upload-button");
    uploadButton.textContent = "Upload";
    uploadButton.disabled = false;

    // remove all previous errors that there might have been there
    document.getElementById("authentication-error-alert").classList.add("hidden");

    // get all input elements for start_screen
    let inputElements = getInputElements();

    // remove feedback from host
    inputElements.host.classList.remove("is-valid");
    inputElements.host.classList.remove("is-invalid");

    // remove feedback from apiToken
    inputElements.apiToken.classList.remove("is-valid");
    inputElements.apiToken.classList.remove("is-invalid");

    // remove feedback from projectName
    inputElements.projectName.classList.remove("is-valid");
    inputElements.projectName.classList.remove("is-invalid");

    // remove feedback from collectionName
    inputElements.collectionName.classList.remove("is-valid");
    inputElements.collectionName.classList.remove("is-invalid");

    // remove feedback from excelFile
    inputElements.excelFile.classList.remove("is-valid");
    inputElements.excelFile.classList.remove("is-invalid");
}
