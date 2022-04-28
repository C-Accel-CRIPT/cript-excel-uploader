# CRIPT Excel Uploader
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  

This repository contains scripts to upload data from a standard Excel template to the CRIPT database.  

### Feedbacks and bug reports welcomed!
### Click the **Share a thought** button in left behind of our [website](https://www.criptapp.org/).

## Download files
Go to the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)
1. Download executable file  
   *Executable files are available for Windows and MacOS.*
   * Windows
      * Download **cript_uploader.exe** 
   * MacOS 
      * Download **cript_uploader** 
      * Having issues running the file?
          * Open a terminal and navigate the relevant folder  
          `cd <path_to_folder>`
          * Change the file permissions  
          `chmod 755 ./cript_excel_uploader`
          * Run it  
          `./cript_excel_uploader`
2. Download configuration file (optional, but more convenient)
   * Download **config.json**
   * **Put config.json in the same directory as executable file**
   * Open the configuration file using notepad
   * Fill the values for the parameters and the excel uploader will read them automatically.
   * Validate your json file in this [website](https://codebeautify.org/jsonvalidator). Make sure it's a valid json.  
     *If you have trouble writing a valid json, see known issues below*
   * Save the **config.json** before you start uploading.
          

## Excel Template

Download **example_template.xlsx** from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)

### Guidelines For Modifying The Template
- **Before we started**
  - Every spreadsheet is a collection.   
    All the data in the single spreadsheet will be saved to the same collection.
  - Ideas behind group, collection, experiment, process is [here](https://criptapp-staging.herokuapp.com/docs/datamodel/)
  - Make sure you have already been a member of a group, and created a collection where the data will be uploaded.

- **Sheet** 
  - The required sheets are marked as **orange**.
  - The optional sheets are marked as **grey**.   
    *You can either keep for future use or remove to simplify if you don't need them*
  - The sheet names **cannot be renamed**, new sheet with other names will be ignored.
  - sheet structure: first row is *column name*, second row is *unit*, others are *values*
- **Column**
  - Columns follow a format like this : \(sign\)(\[identifier\])field1(:field2)(:field3)
    - Sign
      - Columns marked with an asterisk `*` are required (eg. `*name`).
      - Columns marked with a hashtag `#` will be ignored (eg. `#storage`).
    - Identifier
      - Identifier can be a number with square brackets (eg. `[1]`)
      - Identifier is used to allow you to add same property/condition for multiple times.  
      eg. Property `density` is measured multiple times under different temperature. 
        In this case, we can use `[1]density`, `[1]density:temperature`, `[2]density`, `[2]density:temperature`, etc.
    - Field  
      1. Fields can be categorized into following type: 
      - base: defined as parameters in `node.__init__()` function.  
        *Different node has different base nodes*
      - foreign-key: special kind of "base" columns, linked to another nested node  
        *see:* `experiment` *in process sheet (linked to experiment node)*  
        `ingredient` *in process product sheet (linked to material node)*  
        `product` *in process product sheet (linked to material node)*  
        `data` *in file sheet (linked to data node)*  
        `material` *in mixture component sheet (linked to material node)*  
        `component` *in mixture component sheet (linked to material node)*  
        `process` *in prerequisite process sheet (linked to process node)*  
        `prerequisite_process` *in prerequisite process sheet (linked to process node)*  
      - property: defined in property key tables.  
        *Different node has different property key tables.*  
        *see: [material-property-key](https://criptapp-staging.herokuapp.com/docs/datamodel/), [process-property-key](https://criptapp-staging.herokuapp.com/docs/datamodel/)*
      - condition: defined in condition key table.  
        *see: [condition-key](https://criptapp-staging.herokuapp.com/docs/datamodel/)*
      - attribute: defined as parameters in `Property.__init__()` and `Condition.__init__()` function except for `key` and `value`.  
        *see: [property-attribute](https://criptapp-staging.herokuapp.com/docs/datamodel/), [condition-attribute](https://criptapp-staging.herokuapp.com/docs/datamodel/)*
      - quantity: defined in quantity key table used in *process ingredient* sheet.  
        *see: [quantity-key](https://criptapp-staging.herokuapp.com/docs/datamodel/)*
      - identifier: defined in identity key tables used in *material* sheet  
        *see: [material-identifier-key](https://criptapp-staging.herokuapp.com/docs/datamodel/)*
      2. allowed nesting rules  
        nesting is supported for property, condition, attribute and data
      - property:property-attribute eg.`density:method_description`
      - property:condition eg.`density:temperature`
      - property:condition:condition-attribute eg.`density:temperature:uncertainty`
      - property:condition:data eg.`density:temperature:uncertainty`
      - property:data eg.`density:data`
      - condition:condition-attribute eg.`temperature:uncertainty`
      - condition:data eg.`temperature:data`
    - Other rules
      - For `process ingredient` sheet, each ingredient must include one or more quantity defintion.
- **Unit**
  - The value in the second row will be recognized as unit.
  - Supported units are provided in property/condition/quantity key tables.
  - Theoretically you can try any unit you want, If the unit is not support, we will let you know in error detection.
  - The value with the given unit will be standardized after being uploaded.
- **Value**
  - Cross validation is required for the name categorized as "foreign-key".
    Cross validation check tries to match the names in two columns after removing all the space 
    and making every character lower case.
  - The fields in `node.required` should be not null.
  - The fields in `node.unique_together` should be unique in combination.  
    *ignore if there's group or collection since it's predefined*
  - Controlled vocabulary is preferred for type and keyword. 
    You can also customize your own type/keyword by having a `+` sign before them  
    *see: [data-type](https://criptapp-staging.herokuapp.com/docs/datamodel/), [ingredient-keyword](https://criptapp-staging.herokuapp.com/docs/datamodel/), [process-keyword](https://criptapp-staging.herokuapp.com/docs/datamodel/)*
  - For list value, you are allowed to type in multiple values separated by ","
  - Empty rows will be skipped.
  - Processes in the same experiment will be linked together(set as prerequisite process) in order.
  - There's a known issue for string/integer or string/float conversion.
- **We Recommend**
  - Have less than 200 experiments in a single spreadsheet.  
    Or you may have to spend a long time fixing the bugs and uploading.
  - Make backups for your excel spreadsheet and keep them in a safe place.

### Known Issues
- **I have trouble writing a valid json**  
  In most cases which causing an invalid json, have a check whether:
  - Your file path has single backslash```
    \
    ```, if so, replace them with forward slash`/` or double backslash`\\`
  - Your json ends with coma after the value for the last field, remove the coma you should be good.
- **What happened if I run the excel uploader twice**  
  It will do updating stuff in the second time. Old data will be replaced with new one.
- **It looks that I type in a number but the parser gives me an error saying that it reads the number as a string**  
  The issue is caused by having a wrong value type for the given cell.
  Make sure the type for the given cell in the spreadsheet is what it's expected.  
  eg. turn the type for value `5` from `text` to `number` to make sure our excel uploader
  can read it as a number instead of string.
  

## Customize your excel uploader

**Follow the steps below to clone the source code:**
1. [Download Python(>=3.10)](https://www.python.org/)
2. [Download Git](https://git-scm.com/downloads)
3. Open a terminal
4. Install **virtualenv**  
   `pip3 install virtualenv`
5. Create a virtual environment  
   `virtualenv cript-uploader`
6. Activate the virtual environment  
   **Windows:** `cript-uploader\Scripts\activate`  
   **Mac or Linux:** `source cript-uploader\bin\activate`
7. Clone the repository  
   `git clone git@github.com:C-Accel-CRIPT/cript-excel-uploader.git`
8. Change to the project directory  
   `cd cript-excel-uploader`
9. Download requirements  
   `pip install -r requirements.txt`
10. Run the **main.py** file  
    `python main.py`

**Project Structure**  
sheets(data preprocessing and parser) -> validator -> transformer -> uploader 

**Start customize your code now!**
