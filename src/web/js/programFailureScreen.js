/*
this function takes in a list of errors to display and shows them to the user
*/
eel.expose(showProgramFailureError);

function showProgramFailureError(errorList) {
    let errorWindow = document.getElementById("program-failure-error");

    for (let i = 0; i < errorList.length; i++) {
        let errorElement = document.createElement("div");

        errorElement.classList.add("alert");
        errorElement.classList.add("alert-danger");
        errorElement.setAttribute("role", "alert");
        errorElement.textContent = errorList[i];

        errorWindow.appendChild(errorElement);
    }
}