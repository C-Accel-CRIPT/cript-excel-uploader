# Frequently Asked Questions (FAQ)


* **What happens if I run the uploader more than once?**
    * _If the name of an object has not been changed, the existing object will be updated in the database. If the name has been changed, a new object will be created and the old will remain._

* **I entered a number into a cell but the uploader says the value is a string. What gives?**
    * _This is likely caused by the wrong value type being set for the given cell in the Excel document._

* **What units can I use?**
    * _Here is a list of the <a href="https://github.com/hgrecco/pint/blob/master/pint/default_en.txt" target="_blank">supported units</a> from the Pint Python package._

* **What if I have multiple measurements of the same thing?**
    * _You can use an `ID` field in front of row 2 to separate out the different measurements more on that in
    the <a href="excel_rows/#id-optional" target="_blank">ID section of Row 2</a>_

* **Does capitalization make a difference for units?**
    * _Yes the units are very case-sensitive and the program will perceive KPa and kPa as two separate things and can cause errors and issues_

* **What do I need to use the Excel Uploader program?**
    * _You will need to have <a href="https://www.google.com/chrome/" target="_blank">chrome</a> or <a href="https://www.chromium.org/getting-involved/download-chromium/" target="_blank">chromium</a> installed on your computer because Excel Uploader program runs on chrome/chromium_

* **How should I go about fixing errors when I run Excel Uploader program?**
    * _Please be sure you have the latest Excel Uploader program for your operating system, and fix the errors from top down because often the errors that appear further down on the list are a result of the errors at the top of the list_ 

* **Are there additional resources to upload my data to CRIPT?**
    * _You can try:_
        1. _inputting your data directly into [CRIPT](https://criptapp.org) via the user interface_
        2. _using the [CRIPT Python SDK](https://pypi.org/project/cript/) to programmatically upload your data to [CRIPT](https://criptapp.org)_
        3. _getting existing CRIPT Scripts and CRIPT Sheets from [criptscripts.org](https://criptscripts.org)_
