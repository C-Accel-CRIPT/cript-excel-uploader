// get input elements, pack them inside JSON, and return JSON package
function getInputElements() {
    // get all input elements
    const host = document.getElementById("host-input");
    const apiToken = document.getElementById("api-token-input");
    const projectName = document.getElementById("project-name");
    const collectionName = document.getElementById("collection-name");

    const excelFilePath = document.getElementById("excel-file-path");

    return {
        "host": host,
        "apiToken": apiToken,
        "projectName": projectName,
        "collectionName": collectionName,
        "excelFile": excelFilePath
    }
}

function submitForm(event) {
    // get all input values
    const host = document.getElementById("host-input").value;
    const apiToken = document.getElementById("api-token-input").value;
    const projectName = document.getElementById("project-name").value;
    const collectionName = document.getElementById("collection-name").value;
    const excelFilePath = document.getElementById("excel-file-path").value;

    // JSON pack of user input from UI
    const userInput = {
        "host": host,
        "apiToken": apiToken,
        "projectName": projectName,
        "collectionName": collectionName,
        "excelFile": excelFilePath
    }

    // turn the upload button into a spinner

    // submit the form to GUI
    eel.validate_and_set_user_input(userInput)

    // convert button text from "upload" to "Loading ..." and mark it as disabled
    let uploadButton = document.getElementById("upload-button");
    uploadButton.textContent = "Loading ...";
    uploadButton.disabled = true;
}

// variable used to check if tkinter dialog box is already open or not
let isTkinterDialogBoxOpen = false;

// launches a tkinter dialog box and gets the Excel file path
function getFilePathPython() {
    // only open dialog box if not already open
    if (!isTkinterDialogBoxOpen) {
        eel.get_excel_file_path();
    }

    // dialog box is already open and user clicked to open it again
    else {
        console.log("modal is already open");
    }
}

eel.expose(setIsDialogBoxOpen);

// python calls this and sets it to the state of whether dialog box is open or not
function setIsDialogBoxOpen(dialogBoxState) {
    isTkinterDialogBoxOpen = dialogBoxState;
}


// gets excel absolute path from python tkinter and sets the input text value
eel.expose(setExcelFilePath);

function setExcelFilePath(excelAbsolutePath) {
    const excelFilepath = document.getElementById("excel-file-path");
    excelFilepath.value = excelAbsolutePath;
}


eel.expose(displayFormErrors);

/*
    this function is called by validate_and_set_user_input() from eel gui when an input
    from the start_screen.html form is submitted and something does not validate
    then this function is called with a JSON of fields that were invalid
    and the feedback to show to the user

    currently, just using all the html errors, and not inputting that dynamically,
    but the feature exists if needed

    expecting a JSON filled with
    {
      "host": "some error",
      "apiToken": "some error",
      "project" : "some error",
      "collection: "some error",
      "excel_file": "some error",
    }
*/
function displayFormErrors(errors) {
    // hidden alert
    let authenticationAlert = document.getElementById("authentication-error-alert");

    // input elements
    let host = document.getElementById("host-input");
    let apiToken = document.getElementById("api-token-input");
    let projectInput = document.getElementById("project-name");
    let collectionInput = document.getElementById("collection-name");
    let excelFile = document.getElementById("excel-file-path");

    let uploadButton = document.getElementById("upload-button");
    uploadButton.textContent = "Upload";
    uploadButton.disabled = false;


    // if authentication error
    if (errors.host && errors.apiToken) {
        // show the authentication error alert
        authenticationAlert.classList.remove("hidden");

        // give feedback in input fields, for user to understand the issue
        host.classList.add("is-invalid");
        apiToken.classList.add("is-invalid");

        // exit the function because if host and token are invalid then other fields are unknown
        return;
    }
    // if no authentication error
    else {
        // hide authentication error alert if it is showing and the error has been fixed
        authenticationAlert.classList.add("hidden");

        /*
        if form is showing error from last attempt, and errors are fixed,
        then show their input is valid
        */

        host.classList.add("is-valid");
        apiToken.classList.add("is-valid");
    }

    // if project field gives an error
    if (errors.project) {
        projectInput.classList.add("is-invalid");
    }
    // project is valid
    else {
        projectInput.classList.add("is-valid");
    }

    // if collection field gives an error
    if (errors.collection) {
        collectionInput.classList.add("is-invalid");
    }
    // project is valid
    else {
        collectionInput.classList.add("is-valid");
    }

    // file does not exist
    if (errors.excel_file) {
        excelFile.classList.add("is-invalid");
    }
    // file exists
    else {
        excelFile.classList.add("is-valid");
    }

}

/*
    toggle that shows text or password type input

    when clicked, and it is displaying the api token as text,
    it changes the icon to give user feedback that button has been clicked
    and to show in which state the input field is in
 */
function passwordVisibilityToggle() {
    let apiTokenInput = document.getElementById("api-token-input");
    let apiTokenVisibilityToggle = document.getElementById("api-token-visibility-button-icon");

    if (apiTokenInput.type === "password") {
        apiTokenInput.type = "text";
        apiTokenVisibilityToggle.textContent = "visibility_off"
    } else {
        apiTokenInput.type = "password";
        apiTokenVisibilityToggle.textContent = "visibility"
    }
}
