eel.expose(displayCollectionURL);

// gets called from python eel with collection URL and attaches collection URL to dom
function displayCollectionURL(collectionURL) {
    let criptDataLink = document.getElementById("data-in-cript-link");
    criptDataLink.setAttribute("href", collectionURL);
}