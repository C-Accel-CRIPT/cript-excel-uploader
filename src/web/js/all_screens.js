/*
    this event is listening for the browser to be closed.
    After the user clicks to close the browser, this code runs and notifies python eel
    to exit the program
*/
addEventListener('beforeunload', (event) => {
    eel.user_closed_app()
});


/*
this function is called when the python program in the backend exits and is no longer functioning.
This function closes up the GUI so the user doesn't think the program is still running but just frozen
when python has already exited and is done
*/
eel.expose(pythonExitCleanUp);

function pythonExitCleanUp() {
    window.close()
}