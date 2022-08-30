# CRIPT Excel Uploader

## Usage

<!-- TODO be sure to update this picture for every release -->
<img src="./docs_assets/screenshot_of_where_to_find_excel_uploader.png"
alt="Screenshot latest CRIPT release assets">
<small>
Please use the latest release assets
</small>

<br>

### Follow these steps

<ol id="usage-steps">
  <li>
    Login or Signup for the <a href="https://www.criptapp.org/" target="_blank">CRIPT platform</a>
  </li>

  <li>
    Create an <b>Access Group</b> inside of the 
    <a href="https://www.criptapp.org/group" target="_blank">CRIPT platform</a>
    <ul>
      <li>
        An Access Group serves as permission control for the project. It represents an organization, institution, research group, or any grouping of users.
      </li>
      <li>
        An Access Group is needed because every Project must be owned by an Access Group
      </li>
    </ul>
  </li>

  <li>
    Create a <b>Project</b> inside the 
    <a href="https://www.criptapp.org/project" target="_blank">CRIPT platform</a>
    <ul>
      <li>
      <!-- todo define project -->
      A Project can be thought of as a bunch of folders each containing experiments that contribute to a single project
      </li>
      <li>
        Essentially some Collections put in one bucket
      </li>
      <li>
        A Project is needed because each Collection belongs to a Project
      </li>
    </ul>
  </li>

  <li>
    Create a <b>Collection</b> inside the 
    <a href="https://www.criptapp.org/collection" target="_blank">CRIPT platform</a>
    <ul>
      <li>
        <!-- todo is this correct? -->
        A Collection can be thought of as a binder filled with experiments
      </li>
      <li>
      The entire <span style="color: #21a366">Excel</span> file will become a collection within the CRIPT Platform
      </li>
    </ul>
  </li>

  <li>
    Download <code style="color: var(--excel-light-color)">example_template_vX-X-X.xlsx</code> from the 
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases" target="_blank">latest release</a>
    <ul>
      <li>
          The example_template_vX-X-X.xlsx can be used by users to directly record their data in the file
      </li>
      <li>
        Additionally, example_template_vX-X-X.xlsx can serve as an example excel file for users to get an idea on how to structure the excel files they may already have to conform with CRIPT
      </li>
    </ul>
  </li>

  <li>
    Download <code>config.yaml</code> from the 
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases" target="_blank">latest release</a>
    <ul>
      <li>
        Fill out template with your information
      </li>
    </ul>
  </li>

  <li>
  <!-- TODO be sure to keep this version up to date -->
    Download <code>cript_uploader_vX.X.X</code> from <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases" target="_blank">latest release</a>
  <li>
      Be sure all 3 files in the same directory 
      <br>
      <ul>
        <li>
          <code>example_template_vX-X-X.xlsx</code>
        </li>
        <li>
          <code>config.yaml</code>
        </li>
        <li>
        <!-- TODO be sure to always keep this up to date -->
          <code>cript_uploader_vx.x.x</code>
        </li>
      </ul>
    </li>
  <li>
    Run CRIPT Excel Uploader
  </li>
</ol>

---
<br>

---

<br>

### <b> <span class="row-1">Row 1</span> <span class="row-2">Row 2</span> <span class="row-3" style="font-weight: normal;">Row 3</span> </b>

<img src="./docs_assets/screenshot_of_material_sheet_rows_and_columns.png"
alt="Screenshot of Material sheet rows and columns">

The Row 1 - 3 within each <span style="color: var(--excel-light-color)">Excel</span>
sheet are treated differently than Rows 4 - ∞.

<br>

- <span class="row-1">Row 1</span>: Describes the abstract category of Row 2

  > It can be thought of as an abstraction of row 2

#### <u id="row-1-options-list">List of possible options for Row 1</u>

- <span class="row-1">attribute</span>
  - Column with simple key-value pairs
- <span class="row-1">condition</span>
  - Column with key, value, and unit combinations for
  - The condition under which the property was discerned
- <span class="row-1">identifier</span>
  - Column with key-value pairs for material identifiers
- <span class="row-1">property</span>
  - Column with key, value, and unit combinations for properties
- <span class="row-1">relation</span>
  - Column that reference other sheets in the template
- <span class="row-1">quantity</span>
  - Column with key, value and unit combinations for quantities

<br>

> `Relation` is a bit tricky to explain, so we dedicated a section that <a href="#relation-explanation">explains row 1
> abstract category of `relation`</a>

<br>

- <span class="row-2">Row 2</span>: This is the label for each column

  - Eg. `name`, `density`, `bigsmiles`

  - Each label for each sheet column from a controlled list of vocabulary options from CRIPT
    - Each list of controlled vocabulary options will be listed as a link in the
      <a href="#individual-sheets-reference">documentation of each sheet below</a>

<br>

- <span class="row-3">Row 3</span>: Defines the units for that column

  - `celsius`, `g/ml`
  - All the <a href="https://github.com/hgrecco/pint/blob/master/pint/default_en.txt" target="_blank">supported units are
    documented</a>

<br>

---

<br>

### <span id="relation-explanation" class="row-1"><b>relation</b></span> field in row 1 explained

The row 1 field <code>relation</code> is essentially a way for a row from one sheet to reference another row in a
different sheet.

In computer science terms, we could think of it as a foreign key type of relationship from the
<code>relation</code> row of one
sheet to the <code>\*name</code> row of another sheet, the name field works well as an identifier because we are
requiring names to be unique within a given sheet.

<img src="./docs_assets/relation-column-animation-explanation.gif"
alt="video explanation of relation column in an animated format"
width="900">

---

<br>

[//]: # "todo consider putting this section in the section where you explain ROW 1, ROW 2, ROW 3"

### <span class="row-2">row 2</span> <u>Column Field Names</u>

<img src="./docs_assets/screenshot_of_star_required_columns.png"
alt="Screenshot of an Excel column that shows the required column that begins with a *">

<blockquote>
  <ul>
    <li>
      Columns beginning with <code>*</code> are required (eg. <code>*name</code>)
    </li>
    <li>
      Columns beginning with <code>#</code> will be ignored (eg. <code>#storage</code>)
      <ul>
        <li>
          <code>#</code> columns are a good idea to use if you want to have some notes, but don't want it necessarily read or uploaded to CRIPT
        </li>
      </ul>
    </li>
  </ul>
</blockquote>

<br>

Below is a list of
<a href="#individual-sheets-reference">valid values for each sheet's row 2</a>

---

<br>

#### <u>Nesting Headers for each column in row 2</u>

<img src="./docs_assets/Screenshot_nested_row_column_header.png" style="margin-left: 3rem"
alt="Screenshot from Excel sheet column that shows multiple field headers">

- We can have more than one field present on a column header if needed
  - We can indicate that we are recording the `density` at a certain `temperature` by using a colon `":"` and notating
    it like this: `"density:temperature"`
  - Examples
    - Define a material property method: `density:method`
    - Associate data with a process condition `temperature:data`
    - Associate a citation with a material property: `density:citation`
    - Define material property condition: `density:temperature`
    - Define the uncertainty of a material property condition: `density:temperature:uncertainty`
      > `<field>:data` column values should derive from the `*name` column of the `Data` sheet.  
      > `<field>:citation` column values should derive from the `*name` column of the `Citation` sheet.

---

<br>

#### `Id` <span style="color: grey; font-size: 0.8rem;"> - (optional)</span>

`Id` is used to allow for multiple measurements throughout time. With `Id` it is possible to take several measurements
through an experiment, and later use nesting to record more details.

If there are multiple densities throughout time, and we want to show each of their temperatures (or any other
condition) we can use an `Id` field to differentiate between the different temperatures. We denote an `Id` with brackets
and a number inside such as [1] or [2]. The `Id` is used to identify distinct properties/conditions of the same type

- e.g., To identify two density measurements at two different temperatures, we could create the following column
  headers: <span class="row-2">[1]density</span>, <span class="row-2">[1]density:temperature</span>
  , <span class="row-2">[2]density</span>, <span class="row-2">[2]density:temperature</span>

<br>

<table>
  <tr>
    <td class="row-1">
      property
    </td>
    <td class="row-1">
      property:condition
    </td>
    <td class="row-1">
      property
    </td>
    <td class="row-1">
      property:condition
    </td>
  </tr>
  <tr>
    <td class="row-2">
      [1]density
    </td>
    <td class="row-2">
      [1]density:temperature
    </td>
    <td class="row-2">
      [2]density
    </td>
    <td class="row-2">
      [2]density:temperature
    </td>
  </tr>
  <tr class="row-3">
    <th class="row-3">
        g/ml
    </th>
    <th class="row-3-in-table">
      degC
    </th>
    <th class="row-3">
        g/ml
    </th>
    <th class="row-3-in-table">
      degC
    </th>
  </tr>
  <tr class="row-4">
    <td>
      0.87
    </td>
    <td>
      20
    </td>
    <td>
      1
    </td>
    <td>
      30
    </td>
  </tr>
</table>

<!--
Here, we are recording the <span class="row-2">[1]density</span>, and then we are recording the temperature of that
density with <span class="row-2">[1]density:temperature</span> and then we have a different <span class="row-2">[2]
density</span> at a different time and then we are recording the temperature of that density <span class="row-2">[2]
density:temperature</span>
-->

<br>

---

## <span class="row-4">Row 4</span> - ∞

#### <u>Inputting list instead of a single value</u>

List values must use a semicolon **`;`** as a separator

Example:

<table>
  <tr class="row-1">
    <td class="row-1">
      category
    </td>
  </tr>
  <tr>
    <td class="row-2">
      field name
    </td>
  </tr>
  <tr class="row-3">
    <th class="row-3">
        units
    </th>
  </tr>
  <tr class="row-4">
    <td>
      funder 1; funder 2; funder 3; funder 4
    </td>
  </tr>
</table>

<br>

---

## FAQ

- **_What happens if I run the uploader more than once?_**  
  If the name of an object has not been changed, the existing object will be updated in the database. If the name has
  been changed, a new object will be created and the old will remain.

- **_I entered a number into a cell but the uploader says the value is a string. What gives?_**  
  This is likely caused by the wrong value type being set for the given cell in the Excel document.

- **_What units can I use?_**  
  Here is a list of the <a href="https://github.com/hgrecco/pint/blob/master/pint/default_en.txt" target="_blank">supported units</a>
  from the Pint Python package.

<div style="margin-bottom: 5rem;"></div>
