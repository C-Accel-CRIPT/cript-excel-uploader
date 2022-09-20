// get input elements, pack them inside JSON, and return JSON package
function getInputElements() {
    // get all input elements
    const host = document.getElementById("host-input");
    const apiToken = document.getElementById("api-token-input");
    const projectName = document.getElementById("project-name");
    const collectionName = document.getElementById("collection-name");

    // TODO might want to enforce boolean so it can't become anything else in the middle
    const isDataPublic = document.getElementById("public-data");

    const excelFilePath = document.getElementById("excel-file-path");

    return {
        "host": host,
        "apiToken": apiToken,
        "projectName": projectName,
        "collectionName": collectionName,
        "isDataPublic": isDataPublic,
        "excelFile": excelFilePath
    }
}

function submitForm(event) {
    // get all input values
    const host = document.getElementById("host-input").value;
    const apiToken = document.getElementById("api-token-input").value;
    const projectName = document.getElementById("project-name").value;
    const collectionName = document.getElementById("collection-name").value;
    const isDataPublic = document.getElementById("public-data").checked;
    const excelFilePath = document.getElementById("excel-file-path").value;

    // JSON pack of user input from UI
    const userInput = {
        "host": host,
        "apiToken": apiToken,
        "projectName": projectName,
        "collectionName": collectionName,
        "isDataPublic": isDataPublic,
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

// launches a tkinter dialog box and gets the Excel file path
function getFilePathPython() {
    eel.get_excel_file_path();
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

function fillInputDev() {
    let inputElements = getInputElements();
    inputElements.host.value = "";
    inputElements.apiToken.value = "";
    inputElements.projectName.value = "";
    inputElements.collectionName.value = "";
    inputElements.excelFile.value = "";
}

fillInputDev();
