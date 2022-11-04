# CRIPT Excel Template


## Autofill Feature
The Excel template comes with autofill feature. Users can now click on row 2 (column names) and pick from a list of available columns options that each sheet supports. Once an options is selected, row 1 (category), row 3 (unit), and row 4 (instructions) are populated based on the selected option. This way users do not need to think about any other details except what they want to record in the Excel sheets.

The autofill is fairly new and has some drawbacks as well. Firstly, as controlled vocabulary is updated and changed within the <a href="https://criptapp.org/">CRIPT website</a>, 
the Excel sheets does not have the ability to get the newest vocabulary, is unaware of any updates to the <a href="https://criptapp.org/keys/">CRIPT vocabulary</a>, and instead will keep the vocabulary that it came with at the time it was released. 
This could result in the Excel sheet giving validation errors that your new key that you got from <a href="https://criptapp.org/keys/">CRIPT vocabulary</a> is not valid when in fact it is, but Excel is not aware of the changes on the <a href="https://criptapp.org/">CRIPT website</a>, and therefore might give you warnings. If there are any issues with the controlled vocabulary or any errors at all the CRIPT Excel Uploader will show them as errors that you can easily fix.

For most complete and up-to-date list of vocabulary please always check the <a href="https://criptapp.org/keys/">CRIPT vocabulary</a> page.

## Protected sheet

The sheets are protected because rows 1, 3, and 4 contain formulas that we do not want to accidentally delete. If the user feels like they do not want/need the protection they can easily unlock the sheets as the Excel sheets protection do not contain any passwords. Unlocking the sheet can be done several ways but a convenient way is to right-click on the sheet and click unprotect sheet

<img src="../docs_assets/how_to_unprotect_excel_sheet.png" class="screenshot-border"
alt="screenshot of an Excel sheet tab option of how to unprotect an Excel sheet">

## Data validation
Warnings exist and are aimed to help

Do not copy and paste on cells that have data validation because that can create issues

## Excel Web
