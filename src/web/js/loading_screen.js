// TODO needs to do better than stop the entire program and close the window
// TODO consider using multi threading so you can stop the upload
//  and return them to the start screen instead
// when cancel button is clicked, stop the upload, indicate to user that it's been canceled, and return to start screen
function cancelUpload() {
    // when cancel button is clicked indicate to user that their upload has been canceled

    document.getElementById("uploader-progress").textContent = "Canceled";
    eel.cancel_upload();

    // slight delay here so user can see the program canceled instead of a sudden stop
    setTimeout(window.close, 900);
}


// handles updating progress bar and can be called from python code
eel.expose(updateLoadingBar);

function updateLoadingBar(progressNumber) {
    // must change aria-valuenow, text content, style width
    const progressbar = document.getElementById("uploader-progress");

    // converts 10 to 10%
    const progressPercent = `${progressNumber}%`;

    // aria-value-now (accessibility) needs raw number
    progressbar.ariaValueNow = progressNumber;

    // width and text content both use percentage
    progressbar.style.width = progressPercent;
    progressbar.textContent = progressPercent;

    // TODO test make this correct or if it needs to come from python instead
    // if reaches 100% then go to success screen
    if (progressNumber === 100) {

        // slight delay so user can see they reached 100% before navigating to Success screen
        setTimeout(goToSuccessScreen, 1000);
    }
}