function cancelUpload() {
    // when cancel button is clicked indicate to user that their upload has been canceled

    document.getElementById("uploader-progress").textContent = "Canceled";
    eel.cancel_upload();

    // slight delay here so user can see the program canceled instead of a sudden stop
    setTimeout(window.close, 900);
}


// handles updating progress bar and can be called from python code
eel.expose(updateLoadingBar);

function updateLoadingBar(progressNumber, uploadingSpecifics) {
    // must change aria-valuenow, text content, style width
    const progressbar = document.getElementById("uploader-progress");

    // tell the user what is being uploaded currently eg "uploading materials"
    let uploadingLabel = document.getElementById("uploading-specifics");
    uploadingLabel.textContent = uploadingSpecifics;

    // if progress bar tries to go over 100, then I do not let it
    if (progressNumber > 100) {
        console.error(`uploading: ${uploadingSpecifics}; progressNumber is: ${progressNumber}`);
        return;
    }

    // converts 10 to 10%
    const progressPercent = `${progressNumber}%`;

    // aria-value-now (accessibility) needs raw number
    progressbar.ariaValueNow = `${progressNumber}`;

    // width and text content both use percentage
    progressbar.style.width = progressPercent;
    progressbar.textContent = progressPercent;
}


/*
    can be called by other functions to clear out the progress bar, in case of a re-upload
*/
function resetProgressBar() {
    // must change aria-valuenow, text content, style width
    const progressbar = document.getElementById("uploader-progress");

    // converts 10 to 10%
    const progressPercent = "0%";

    // aria-value-now (accessibility) needs raw number
    progressbar.ariaValueNow = "0";

    // width and text content both use percentage
    progressbar.style.width = progressPercent;
    progressbar.textContent = progressPercent;

    // reset progress bar label to "uploading ..."
    let uploadingLabel = document.getElementById("uploading-specifics");
    uploadingLabel.textContent = "...";
}