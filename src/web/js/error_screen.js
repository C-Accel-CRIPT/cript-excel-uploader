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
    function that fires when the user clicks on the button from the error screen "Try again"
    1. enable the start screen "Upload" button if it may have been changed to "Loading .."
    2. show start screen
    3. empty the errors that were on the error screen, so they do not show up again from last time
*/
function tryAgain() {
    // enable the start screen button
    let uploadButton = document.getElementById("upload-button");
    uploadButton.textContent = "Upload";
    uploadButton.disabled = false;

    // show start screen
    goToStartScreen();

    // empty the errors that were on the error screen, so they do not show up again
    document.getElementById("error-window").innerHTML = "";

    // start progress bar from 0, so it doesn't start from where it left off
    resetProgressBar();
}
