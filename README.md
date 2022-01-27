# CRIPT Excel Uploader
This repository contains scripts to upload data from a standard Excel template to the CRIPT database.

**IMPORTANT!**  
DO NOT delete your Excel documents after running the uploader!  
All data is currently being uploaded to a test database, thus is at risk of being deleted.

## Usage

Executables are available for Windows and MacOS in the **files/** directory.  
These can be downloaded and run without installing Python or any other dependency.

* **Windows**
    * Download [cript_uploader.exe]()

* **MacOS** 
    * Download [cript_uploader]()
    * Having issues running the file?
        * Open a terminal and navigate the relevant folder  
        `cd <path_to_folder>`
        * Change the file permissions  
        `chmod 755 ./cript_uploader`
        * Run it  
        `./cript_uploader`

Alternatively, you can do things the hard way:

1. **Python 3.10** or [Download Latest Release of Python](https://www.python.org/)
2. **Git 2.34** or [Download Latest Release of Git](https://git-scm.com/downloads)
3. Open a terminal
4. Install **virtualenv**  
`pip3 install virtualenv`
5. Create a virtual environment  
`virtualenv cript_uploader`
6. Activate the virtual environment  
**Windows:** `cript_uploader\Scripts\activate`  
**Mac or Linux:** `source cript_uploader\bin\activate`
7. Clone the repository  
`git clone git@github.com:C-Accel-CRIPT/cript_excel_uploader.git`
8. Change to the project directory  
`cd cript_excel_uploader`
9. Download requirements  
`pip install -r requirements.txt`
10. Run the **main.py** file  
`python main.py`

## Excel Template

Download the [example Excel template]() from the **files/** directory.


### Guidelines For Modifying The Template

 - The sheet names cannot be renamed.
 - Columns marked with an asterisk (*) are required.
 - Columns marked with a hash (#) will be ignored.
 - Columns must only use approved key names (see **Column Keys**)
 - All keys are assumed to be using our chosen standard units (see **Key Tables**)
 - Condition keys can be associated with property keys by using a colon (e.g., density:temp)
 - Data can be associated with a property or condition key by using a colon (e.g., density:data)
 - For the **Process Ingredient** sheet, each ingredient must include one or more quantity defintion (see the **Ingredient Quantity** table)
 

### Key Tables

* Column Keys
    * [Reaction Properties](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/property_keys_reaction.html)
    * [Material Properties](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/property_keys_materials.html)
    * [Conditions](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/condition_keys.html)
    * [Ingredient Quantity](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/quantity_keys.html)
* Value Keys
    * [Methods](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/method_keys.html)    
    * [Data Types](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/data_keys.html)
    * [Ingredient Keywords](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/ingredient_keys.html)
    * [Process Keywords](http://htmlpreview.github.io/?https://github.com/C-Accel-CRIPT/cript_tutorials/blob/master/key_tables/process_keys.html)


