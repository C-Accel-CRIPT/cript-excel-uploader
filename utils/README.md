# Script to generate `Material Sheet` controlled vocabulary

## Description

This is the implementation that generates all the options for the Excel Uploader material sheet.

This code is only for the material sheet because the other sheets do not have nesting and can just be copied and pasted from the online controlled vocabulary.

## How it works
It works by:
1. Getting the controlled vocabulary from CRIPT by copying each part and pasting it into the `source.xlsx` sheets
2. `material_sheet_keys.py` generates all the options by:
   1. reading each sheet of the `source.xlsx` file
   2. converting each sheet into a df
   3. running an algorithm to generate all the controlled vocabulary options up to 2 levels deep eg `property:condition`
   > Note: It does not include any ids for the options eg `[1]property:condition`
3. After creating all the options, then it outputs it into a new file called `utils/excel_files/output.xlsx`
4. The developer can then copy the options generated in the `output.xlsx` and paste them into the hidden sheet of the `CRIPT_template.xlsx`