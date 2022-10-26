/*
// takes a string error and creates it into a good html error and attaches it to screen
result is:
    <div class="alert alert-danger" role="alert">
        <b>Sheet:</b> Material
        <br>

        <b>Column:</b> H
        <br>

        <b>Row:</b> 14
        <br>

        <b>Issue:</b> sample_preparation does not have a corresponding data node
    </div>
*/
eel.expose(addErrorsToScreen);

function addErrorsToScreen(errorList) {

    let errorWindow = document.getElementById("error-window");

    for (let i = 0; i < errorList.length; i++) {
        let errorElement = document.createElement("div");

        errorElement.classList.add("alert");
        errorElement.classList.add("alert-danger");
        errorElement.setAttribute("role", "alert");
        errorElement.textContent = errorList[i];

        errorWindow.appendChild(errorElement);
    }

}

/*
    this function runs when user clicks on "Try Again" to try re-uploading
    restarts the start_screen, loading_screen, globus_screen, and error_screen
    calls the eel function to clear out the error_list so there are no old errors
    from previous upload attempt, and sets the current_progress to 0 so the progress bar
    can start from 0 and not from 100
    then takes the user to the start_screen
*/
function tryAgain() {
    restartAllScreens();
    eel.reset_for_uploading()
    goToStartScreen();
}

/*
    restarts the start_screen, loading_screen, globus_screen, and error_screen
*/
function restartAllScreens() {
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
