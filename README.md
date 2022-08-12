# CRIPT Excel Uploader
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  

This code is used to upload a dynamic Excel template to the [CRIPT platform](https://www.criptapp.org/).

<br>
<br>

## Usage

### Excel Template
- Download **example_template_vX-X-X.xlsx** from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)

<br>

### Config File
> Used to define required variables (e.g., `path` to the Excel template).   

- Download the **config.yaml** template from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases).  
- Place the file in the same directory as the executable or Python script. 
- Fill out template with your info.

<br>

### Uploader 
- **Windows**
    - Download **cript_uploader_vX-X-X.exe** from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)
    - Open a terminal and navigate the relevant folder  
    `cd <path_to_folder>`  
    - Run it  
    `.\cript_uploader_vX-X-X.exe`  

- **MacOS** 
    - Download **cript_uploader_vX-X-X** from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)  
    - Open a terminal and navigate the relevant folder  
    `cd <path_to_folder>`  
    - Change the file permissions  
    `chmod 755 ./cript_uploader`  
    - Run it  
    `./cript_uploader_vX-X-X`  

Alternatively, you can do things the hard way:

1. [Download Python(>=3.10)](https://www.python.org/)
2. [Download Git](https://git-scm.com/downloads)
3. Open a terminal
4. Install **virtualenv**  
`pip install virtualenv`
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

<br>
<br>

## Modify Excel Template

### General
- A `Project` and `Collection` must be created in the [CRIPT platform](https://www.criptapp.org/) before running the uploader.
- Each Excel document corresponds to a single `Collection`.

<br>

### Column Headers

#### **Row 1 - Header Type**
The first header row defines the column type and mirrors the key headers (row 2).  
e.g., `property:relation` --> `density:data`

- `relation`
  - Column that reference other sheets in the template.
- `attribute`
  - Column with simple key-value pairs.
- `property`
  - Column with key, value, and unit combinations for properties.
- `condition`
  - Column with key, value, and unit combinations for conditions.
- `identifier`
  - Column with key-value pairs for material identifiers.
- `quantity`
  - Column with key, value and unit combinations for quantities.

#### **Row 2 - Header Key**
The second row defines the key for a column.  
e.g., `name`, `density`, `bigsmiles`  

#### **Row 3 - Header Key Unit**
The third row defines the unit for a column.  
e.g., `celsius`, `g/ml`  

<br>

### Column Header Key Format
[`Id`]`Field`:`Field`:`Field`
> Columns beginning with `*` are required (eg. `*name`).  
> Columns beginning with `#` will be ignored (eg. `#storage`).  

`Id` - *optional*
- Integer used to identify distinct properties/conditions of the same type.
- e.g., To identify two density measurements at two different temperatures, we could create the following column headers: `[1]density`, `[1]density:temperature`, `[2]density`, `[2]density:temperature`

`Field` - *at least one is required*
- See the **Sheets** section for valid values.
- Nested fields can be indicated by placing `:` between the parent and child fields.
    - Examples
        - Define a material property method: `density:method`
        - Associate data with a process condition `temperature:data`
        - Associate a citation with a material property: `density:citation`
        - Define material property condition: `density:temperature`
        - Define the uncertainty of a material property condition: `density:temperature:uncertainty`
        > `<field>:data` column values should derive from the `*name` column of the `Data` sheet.  
        > `<field>:citation` column values should derive from the `*name` column of the `Citation` sheet.

<br>

### Sheets
- Sheets **cannot be renamed**.
> List values must use a semicolon (`;`) as a separator.  
> e.g., `styrene; vinylbenzene; phenylethylene; ethenylbenzene`

#### `material` sheet
Define all materials that will be referenced throughout the document.
| Key | Key Type | Required | Expected Value
| --- | --- | --- | --- |
| *name | attribute | yes | unique string |
| any [identifier key](https://criptapp.org/keys/material-identifier-key/) | identifier | no | refer to key table |
| any [material property key](https://criptapp.org/keys/material-property-key/) | property | no | refer to key table |
| notes | attribute | no | string |

#### `mixture component` sheet -- *optional*
Define the components of mixture materials.   
> The mixture and all component materials must first be defined in the `material` sheet.

| Key | Key Type | Required | Expected Value
| --- | --- | --- | --- |
| *mixture | relation | yes | value from `*name` column of `material` sheet |
| *material | relation | yes | value from `*name` column of `material` sheet | 

#### `experiment` sheet
Define the experiments.
| Key | Key Type | Required | Value Type
| --- | --- | --- | --- |
| *name | attribute | yes | unique string |
| funding | attribute | no | list of strings (e.g, `str1; str2; str3`)
| notes | attribute | no | string |

#### `process` sheet
Define the processes of each experiment.
| Key | Key Type | Required | Expected Value |
| --- | --- | --- | --- |
| *experiment | relation | yes | value from `*name` column of `experiment` sheet |
| *name | attribute | yes | unique string | unique |
| *type | attribute | yes | any [process type](https://criptapp.org/keys/process-type/)
| keywords | attribute | no | list of [keywords](https://criptapp.org/keys/process-keyword/) (e.g, `str1; str2; str3`)
| description | attribute | no | string |
| any [process property key](https://criptapp.org/keys/process-property-key/) | property | no | refer to key table |
| any [condition key](https://criptapp.org/keys/condition-key/) | condition | no | refer to key table |
| notes | attribute | no | string |

### `process equipment` sheet
Define the equipment used in a process.
| Key | Key Type | Required | Expected Value |
| --- | --- | --- | --- |
| *process | relation | yes | value from `*name` column of `process` sheet |
| *key | attribute | yes | any [equipment key](https://criptapp.org/keys/equipment-key/)
| description | attribute | no | string |
| any [condition key](https://criptapp.org/keys/condition-key/) | condition | no | refer to key table |
| *citation | relation | yes | value from `*name` column of `citation` sheet |

#### `prerequisite process` sheet -- *optional*
Define the immediate prerequisites for each process.
> e.g., Assuming `A -> B -> C`, the immediate prerequisite of `C` is `B` (not `A`).  

| Key | Key Type | Required | Value Type
| --- | --- | --- | --- |
| *process | relation | yes | value from `*name` column of `process` sheet |
| *prerequisite | relation | yes | value from `*name` column of `process` sheet |

#### `process ingredient` sheet
Define the ingredients for each process and their respective quantities.
| Key | Key Type | Required | Value Type
| --- | --- | --- | --- |
| *process | relation | yes | value from `*name` column of `process` sheet |
| *material | relation | yes | value from `*name` column of `material` sheet |
| *keyword | attribute | yes | any [ingredient keyword](https://criptapp.org/keys/ingredient-keyword/)
| any [quantity key](https://criptapp.org/keys/quantity-key/) | quantity | yes | refer to key table |

#### `process product` sheet
Define the material products of each process.
| Key | Key Type | Required | Value Type
| --- | --- | --- | --- |
| *process | relation | yes | value from `*name` column of `process` sheet |
| *material | relation | yes | value from `*name` column of `material` sheet |

#### `data` sheet
Define the data sets you will be associating with properties, etc.
| Key | Key Type | Required | Value Type
| --- | --- | --- | --- |
| *experiment | relation | yes | value from `*name` column of `experiment` sheet |
| *name | attribute | yes | unique string | unique |
| *type | attribute | yes | any [data type](https://criptapp.org/keys/data-type/)
| *source | attribute | yes | local file path or external URL |
| sample_preparation | relation | no | value from `*name` column of `process` sheet |
| citation | relation | no | value from `*name` column of `citation` sheet
| notes | attribute | no | string | |

#### `citation` sheet
Define references to be associated with properties, etc. as citations.
| Key | Key Type | Required | Value Type
| --- | --- | --- | --- |
| *title | attribute | yes | unique string |
| doi | attribute | no | string |
| authors | attribute | no | string |
| journal | attribute | no | string |
| publisher | attribute | no | string |
| year | attribute | no | attribute | string |
| volume | attribute | no | string |
| issue | attribute | no | string |
| pages | attribute | no | string |
| issn | attribute | no | string |
| arxiv_id | attribute | no | string |
| pmid | attribute | no | string |
| website | attribute | no | string |
| notes | attribute | no | string |

<br><br>

## FAQ
- ***What happens if I run the uploader more than once?***  
  If the name of an object has not been changed, the existing object will be updated in the database. If the name has been changed, a new object will be created and the old will remain.

- ***I entered a number into a cell but the uploader says the value is a string. What gives?***  
  This is likely caused by the wrong value type being set for the given cell in the Excel document.