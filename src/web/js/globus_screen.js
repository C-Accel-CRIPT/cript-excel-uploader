eel.expose(setGlobusAuthlink);

function setGlobusAuthlink(globusLink) {
    let globusAuthLink = document.getElementById("globus-auth-link");
    globusAuthLink.href = globusLink;
}


/*
 when clicked on the visibility icon, this function fires and toggles the password visibility,
 from password to regular text, so they can see their inputs
*/
function globusAuthVisibilityToggle() {
    let globusAuthToken = document.getElementById("globus-auth-token-input");

    if (globusAuthToken.type === "password") {
        globusAuthToken.type = "text";
    } else {
        globusAuthToken.type = "password";
    }
}

/*
takes user input from dom and sends it to python eel
*/
function submitGlobusAuthToken() {
    let globusToken = document.getElementById("globus-auth-token-input");

    eel.globus_auth_token_validation(globusToken.value);
}