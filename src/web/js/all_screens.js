/*
    this event is listening for the browser to be closed.
    After the user clicks to close the browser, this code runs and notifies python eel
    to exit the program
*/
addEventListener('beforeunload', (event) => {
    eel.user_closed_app()
});