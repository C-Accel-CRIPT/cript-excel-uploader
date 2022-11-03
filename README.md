# Updating Excel Uploader Docs

## Technologies
* The documentation for Excel Uploader utilizes [material mkdocs](https://squidfunk.github.io/mkdocs-material/).

## Files
* **_mkdocs.yml_**
  * contains settings, plugins, theme that is used throughout the documentation
  * contains the navigation for the whole documentation
* **_requirements_docs.txt_**
  * contains all python packages needed for the documentation
  * GitHub actions installs all requirements.txt whenever triggered
* **_docs/_**
  * contains all the documentation written in markdown and html
  * Note: please attempt to make every link open into a new page to optimize for UX, so the user does not lose where they were reading as they are navigated to a new page
  * Colors, icons, diagram, charts can be a helpful way of explaining concepts
* **_docs/stylesheets/extra.css_**
  * contains the css that every page has

## CI/CD
* Any time there is a push to the docs branch GitHub actions the docs gets compiled and deployed to the [CRIPT Excel Uploader documentation](https://c-accel-cript.github.io/cript-excel-uploader/)

