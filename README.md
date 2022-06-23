# CRIPT Excel Uploader
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)  

This code is used to upload a semi-dynamic Excel template to the [CRIPT platform](https://www.criptapp.org/).

<br><br>

## Download

### Template
Download **example_template_vX.X.X.xlsx** from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)

### Uploader
> Executables are available for Windows and MacOS.  
> These can be downloaded and run without installing Python or any other dependency.

- **Windows**
    - Download **cript_uploader.exe** from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)

- **MacOS** 
    - Download **cript_uploader** from the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)
    - Having issues running the file?
        - Open a terminal and navigate the relevant folder  
        `cd <path_to_folder>`
        - Change the file permissions  
        `chmod 755 ./cript_uploader`
        - Run it  
        `./cript_uploader`

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

<br><br>

## Modify Excel Template
### General
- A `Group` and `Collection` must be created in the [CRIPT platform](https://www.criptapp.org/) before running the uploader.
- Each Excel document corresponds to a single `Collection`.

### Column Header Format
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

### Sheets
- Required sheets are colored orange.
- Optional sheets are colored grey (can be removed).
- Sheets **cannot be renamed**.
- First row of every sheet is used for column headers.
- Second row of every sheet is used for unit definitions (leave blank if N/A).

#### `Material` sheet
Define all materials that will be referenced throughout the document.
| Name | Required | Expected Value
| --- | --- | --- |
| *name | yes | unique string |
| any [identifier key](https://criptapp.org/keys/material-identifier-key/) | no | refer to key table |
| any [material property key](https://criptapp.org/keys/material-property-key/) | no | refer to key table |
| notes | no | string |

#### `Mixture Component` sheet -- *optional*
Define the components of mixture materials.   
> The mixture and all component materials must first be defined in the `Material` sheet.

| Name | Required | Expected Value
| --- | --- | --- |
| *material | yes | string from `*name` column of `Material` sheet |
| *component | yes | string from `*name` column of `Material` sheet | 

#### `Experiment` sheet
Define the experiments.
| Name | Required | Value Type
| --- | --- | --- |
| *name | yes | unique string |
| funding | no | list of strings (e.g, `str1, str2, str3`)
| notes | no | string |

#### `Process` sheet
Define the processes of each experiment.
| Name | Required | Expected Value |
| --- | --- | --- |
| *experiment | yes | string from `*name` column of `Experiment` sheet |
| *name | yes | unique string | unique |
| keywords | no | list of [keyword key](https://criptapp.org/keys/process-keyword/) names (e.g, `str1, str2, str3`)
| description | no | string |
| equipment | no | list of [equipment key](https://criptapp.org/keys/equipment/) names (e.g, `str1, str2, str3`) |
| any [process property key](https://criptapp.org/keys/process-property-key/) | no | refer to key table |
| any [condition key](https://criptapp.org/keys/condition-key/) | no | refer to key table |
| notes | no | string |

#### `Prerequisite Process` sheet -- *optional*
Define the immediate prerequisites for each process.
> e.g., Assuming `A -> B -> C`, the immediate prerequisite of `C` is `B` (not `A`).  

| Name | Required | Value Type
| --- | --- | --- |
| *process | yes | string from `*name` column of `Process` sheet |
| *prerequisite_process | yes | string from `*name` column of `Process` sheet |

#### `Process Ingredient` sheet
Define the ingredients for each process and their respective quantities.
| Name | Required | Value Type
| --- | --- | --- |
| *process | yes | string from `*name` column of `Process` sheet |
| *material | yes | string from `*name` column of `Material` sheet |
| *keyword | yes | any [ingredient keyword](https://criptapp.org/keys/ingredient-keyword/)
| any [quantity key](https://criptapp.org/keys/quantity-key/) | yes | refer to key table |

#### `Process Product` sheet
Define the material products of each process.
| Name | Required | Value Type
| --- | --- | --- |
| *process | yes | string from `*name` column of `Process` sheet |
| *product | yes | string from `*name` column of `Material` sheet |

#### `Data` sheet
Define the data sets you will be associating with properties, etc.
| Name | Required | Value Type
| --- | --- | --- |
| *experiment | yes | string from `*name` column of `Experiment` sheet |
| *name | yes | unique string | unique |
| *type | yes | any [data type](https://criptapp.org/keys/data-type/)
| sample_prep | no | string
| citation | no | string from `*name` column of `Citation` sheet
| notes | no | string | |

#### `File` sheet
Define the raw files you will be associating with each data set.
| Name | Required | Value Type
| --- | --- | --- |
| *data | yes | string from `*name` column of `Data` sheet |
| *source | yes | local file path string |
| type | no | any [file type](https://criptapp.org/keys/file-type/)

#### `Citation` sheet
Define references to be associated with properties, etc. as citations.
| Name | Required | Value Type
| --- | --- | --- |
| *title | yes | unique string |
| doi | no | string |
| authors | no | string |
| journal | no | string |
| publisher | no | string |
| year | no | string |
| volume | no | string |
| issue | no | string |
| pages | no | string |
| issn | no | string |
| arxiv_id | no | string |
| pmid | no | string |
| website | no | string |
| notes | no | string |

<br><br>

### FAQ
- ***What happens if I run the uploader more than once?***  
  If the name of an object has not been changed, the existing object will be updated in the database. If the name has been changed, a new object will be created and the old will remain.

- ***I entered a number into a cell but the uploader says the value is a string. What gives?***  
  This is likely caused by the wrong value type being set for the given cell in the Excel document.