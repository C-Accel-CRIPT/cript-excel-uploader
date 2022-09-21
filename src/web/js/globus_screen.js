eel.expose(setGlobusAuthlink);

function setGlobusAuthlink(globusLink) {
    let globusAuthLink = document.getElementById("globus-auth-link");
    globusAuthLink.href = globusLink;
}