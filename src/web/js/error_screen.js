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
