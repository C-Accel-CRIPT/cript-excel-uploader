# Updating Excel Uploader Docs

## CI/CD
Every time a push is made to the **docs** branch, a GitHub actions watching **docs** branch for changes automatically starts running, builds the documentation, and pushes it to **gh-pages** branch. The **gh-pages** branch is also being watched for changes, and any time there is a change then it reloads the documentation website based off of the new push to **gh-pages** branch.

The GitHub actions file for building of the docs can be found in _.github/workflows/docs.yml_, it largely comes from the [Material MkDocs documentation regarding CI/CD](https://squidfunk.github.io/mkdocs-material/publishing-your-site/#with-github-actions)



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

