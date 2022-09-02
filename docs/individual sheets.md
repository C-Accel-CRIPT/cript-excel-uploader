# Customizing the <span style="color: var(--excel-light-color)">Excel</span> Sheets

<img src="../docs_assets/screenshot_of_excel_sheets.png"
alt="screenshot of the Excel sheets to show required and optional sheets">

- Required sheets are colored
  <span class="required-excel-sheet-color"> Orange </span>

- Optional sheets are colored
  <span class="optional-excel-sheet-color"> Grey </span>

<br>

> **Sheets CANNOT be renamed**, but **sheets CAN be removed**

<br>

## The general structure for all sheets

<blockquote>
    <table>
      <tr>
        <td class="row-1">
            <a href="/excel rows/#row-1-options-list">
              abstract category
            </a>
        </td>
      </tr>
      <tr>
        <td class="row-2">
            <a href="/individual sheets/#sheets">
              field name
            </a>
        </td>
      </tr>
      <tr class="row-3">
        <th class="row-3">
            <a href="https://github.com/hgrecco/pint/blob/master/pint/default_en.txt" target="_blank">
              units
            </a>
        </th>
      </tr>
      <tr class="row-4">
        <td>
          <em>Your values</em>
        </td>
      </tr>
    </table>
</blockquote>

<br>

---

## Sheets

#### <span class="required-excel-sheet-color"><u>material</u></span> sheet

<br>

Define all materials that will be referenced throughout the document.

| Row 2                                                                                                 | Row 1      | Required | Row 4 - ∞ expected value                                                                              |
|-------------------------------------------------------------------------------------------------------|------------|----------|-------------------------------------------------------------------------------------------------------|
| \*name                                                                                                | attribute  | yes      | unique name                                                                                           |
| pick from `Name` column of [material identifiers](https://criptapp.org/keys/material-identifier-key/) | identifier | no       | pick a name from the [identifier chart](https://criptapp.org/keys/material-identifier-key/)           |
| pick from `Name` column of [material properties](https://criptapp.org/keys/material-property-key/)    | property   | no       | pick from name column of  [material property chart](https://criptapp.org/keys/material-property-key/) |
| notes                                                                                                 | attribute  | no       | regular text                                                                                          |

<br>

> options for each row are clickable links in the chart below:

<table>
  <tr>
    <td class="row-1">
      <a class="row-1" href="/excel rows/#row-1-options-list" style="color: blue">
        <em><u>supported abstract categories</u></em>
      </a>
    </td>
  </tr>
  <tr>
    <td class="row-2">
    <a class="row-2" href="https://criptapp.org/keys/material-property-key/" target="_blank" style="color: blue">
      <em><u>supported column field names</u></em>
    </a>
    </td>
  </tr>
  <tr>
    <th class="row-3-in-table">
      <a href="https://github.com/hgrecco/pint/blob/master/pint/default_en.txt" target="_blank" style="color: blue">
        <em><u>supported units</u></em>
      </a>
    </th>
  </tr>
  <tr>
    <td class="row-4">
      <em>Your values recorded</em>
    </td>
  </tr>
</table>

<br>

---

<br>

#### <span class="optional-excel-sheet-color"><u>mixture component</u></span> sheet <span style="color: grey; font-size: 0.8rem;">(optional)</span>

This sheet Defines the components of mixture materials.

<br>

<blockquote>
  Before recording any mixtures, the components and materials must be first defined in 
  <span class="required-excel-sheet-color">materials</span> sheet.
</blockquote>

Row 1 is always <code>relation</code> and Row 2 is always
<code>*mixture</code> and <code>*material</code>

<blockquote>
  Row 1 is always <code>relation</code>, because each column of the
  <span class="optional-excel-sheet-color">mixture</span> sheet <b>MUST</b> reference the <span class="required-excel-sheet-color">material</span> sheet
</blockquote>

<br>

| Row 2      | Row 1    | Required | Row 4 - ∞ expected value                      |
|------------|----------|----------|-----------------------------------------------|
| \*mixture  | relation | yes      | value from `*name` column of `material` sheet |
| \*material | relation | yes      | value from `*name` column of `material` sheet |

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *mixture
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *material
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
  </tr>
  <tr>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
  </tr>
  <tr>
    <td class="row-4 user-input-row">
      value comes from *name of <span class="required-excel-sheet-color">mixture</span> sheet
    </td>
    <td class="row-4 user-input-row">
      value from *name of <span class="required-excel-sheet-color">materials</span> sheet
    </td>
  </tr>
</table>

---

<br>

#### <span class="required-excel-sheet-color"><u> experiment</u></span> sheet

This sheet defines the experiment

| Row 2   | Row 1     | Required | Row 4 - ∞ expected value                                |
|---------|-----------|----------|---------------------------------------------------------|
| \*name  | attribute | yes      | unique name                                             |
| funding | attribute | no       | list of your funders (e.g, `funder1; funder2; funder3`) |
| notes   | attribute | no       | regular text                                            |

<br>

> If there are multiple sources for funding please list them and separate each one with a `";"`
> (e.g, `Grants; NSF; IRIS`)

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *name
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      notes 
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      funding 
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
  </tr>
  <tr>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
  </tr>
  <tr>
    <td class="row-4 row-4-required-optional-label">
      unique experiment name
    </td>
    <td class="row-4 row-4-required-optional-label">
      These are my notes
    </td>
    <td class="row-4 row-4-required-optional-label">
      funder 1; funder 2; funder 3; funder 4;
    </td>

  </tr>
</table>

---

<br>

#### <span class="required-excel-sheet-color"><u>process</u></span> sheet

Define the processes of each experiment.

| Row 2                                                                                          | Row 1     | Required | Row 4 - ∞ expected value                                                                                                                    |
|------------------------------------------------------------------------------------------------|-----------|----------|---------------------------------------------------------------------------------------------------------------------------------------------|
| \*experiment                                                                                   | relation  | yes      | value from `*name`column of`experiment` sheet                                                                                               |
| \*name                                                                                         | attribute | yes      | unique name                                                                                                                                 |
| \*type                                                                                         | attribute | yes      | pick from `Name` column of [Process Type](https://criptapp.org/keys/process-type/)                                                          |
| keywords                                                                                       | attribute | no       | list from `Name` column of [Process keywords](https://criptapp.org/keys/process-keyword/) (e.g, `anionic; annealing_sol; annealing_thermo`) |
| description                                                                                    | attribute | no       | regular text                                                                                                                                |
| equipment                                                                                      | attribute | no       | list of [equipments](https://criptapp.org/keys/equipment/) (e.g, `equipment1; equipment2; equipment3`)                                      |
| pick from `Name` column of [process property](https://criptapp.org/keys/process-property-key/) | property  | no       | record your values                                                                                                                          |
| pick from `Name` column of [conditions](https://criptapp.org/keys/condition-key/)              | condition | no       | record your values                                                                                                                          |
| notes                                                                                          | attribute | no       | regular text                                                                                                                                |

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">
        property
      </u> 
    </td>
    <td class="row-1">
      <u class="row-1">condition</u> 
    </td>
    <td class="row-1">
      <u class="row-1">condition</u> 
    </td>

  </tr>
  <tr>
    <td class="row-2">
      *experiment
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *name 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *type 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      keywords
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      <a href="https://criptapp.org/keys/process-property-key/" target="_blank">process property</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>    
    <td class="row-2">
      <a href="https://criptapp.org/keys/condition-key/" target="_blank">any condition value</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      <a href="https://criptapp.org/keys/condition-key/" target="_blank">any condition value</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>

  </tr>
  <tr>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3-in-table">
      <div>units</div>
    </th>
    <th class="row-3-in-table">
      <div>units</div>
    </th>

  </tr>
  <tr>
    <td class="row-4 row-4-required-optional-label">
      value from *name column of <span class="required-excel-sheet-color">experiment</span> sheet
    </td>
    <td class="row-4 row-4-required-optional-label">
      pick your own unique process name
    </td>
    <td class="row-4 row-4-required-optional-label">
      pick from Name column of <a href="https://criptapp.org/keys/process-type/">Process Type</a>
    </td>
    <td class="row-4 row-4-required-optional-label">
      anionic; annealing_sol; annealing_thermo
    </td>
    <td class="row-4 row-4-required-optional-label">
      description of my process
    </td>
    <td class="row-4 row-4-required-optional-label">
      100.0
    </td>
    <td class="row-4 row-4-required-optional-label">
      55.26
    </td>

  </tr>
</table>

<br> <br>

Example:

<blockquote>
<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">condition</u> 
    </td>
    <td class="row-1">
      <u class="row-1">condition</u> 
    </td>

  </tr>
  <tr>
    <td class="row-2">
      *experiment
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *name 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *type 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      keywords
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      description
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>    
    <td class="row-2">
      temperature
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      time_duration
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>

  </tr>
  <tr>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3-in-table">
      <div>degC</div>
    </th>
    <th class="row-3-in-table">
      <div>min</div>
    </th>

  </tr>
  <tr>
    <td class="row-4 row-4-required-optional-label">
      value from *name column of <span class="required-excel-sheet-color">experiment</span> sheet
    </td>
    <td class="row-4 row-4-required-optional-label">
      pick a unique process name
    </td>
    <td class="row-4 row-4-required-optional-label">
      anionic; annealing_sol; annealing_thermo
    </td>
    <td class="row-4 row-4-required-optional-label">
      my keywords to find my process
    </td>
    <td class="row-4 row-4-required-optional-label">
      description of my process
    </td>
    <td class="row-4 row-4-required-optional-label">
      100.0
    </td>
    <td class="row-4 row-4-required-optional-label">
      55.26
    </td>

  </tr>
</table>

</blockquote>

---

<br>

#### <span class="optional-excel-sheet-color">process equipment</span> sheet <span style="color: grey; font-size: 0.8rem;">(optional)</span>

Define the equipment used in a process.

| Row 2                                                                             | Row 1     | Required | Row 4 - ∞ expected value                                                          |
|-----------------------------------------------------------------------------------|-----------|----------|-----------------------------------------------------------------------------------|
| \*process                                                                         | relation  | yes      | value from `*name` column of `process` sheet                                      |
| \*equipment                                                                       | attribute | yes      | pick from `Name` column of [equipments](https://criptapp.org/keys/equipment-key/) |
| description                                                                       | attribute | no       | regular text                                                                      |
| pick from `Name` column of [conditions](https://criptapp.org/keys/condition-key/) | condition | no       | record your values                                                                |
| \*citation                                                                        | relation  | yes      | value from `*name` column of `citation` sheet                                     |

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">condition</u> 
    </td>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *process
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
        <a href="https://criptapp.org/keys/equipment-key/" target="_blank">*select equipment</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>    
    <td class="row-2">
      description
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      <a href="https://criptapp.org/keys/condition-key/" target="_blank">condition</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
        citation
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
  </tr>
  <tr>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3-in-table">
      <a style="color: blue" href="https://github.com/hgrecco/pint/blob/master/pint/default_en.txt" target="_blank">supported units</a>
    </th>
    <th class="row-3-in-table">
      <div></div>
    </th>
  </tr>
  <tr>
    <td class="row-4 row-4-required-optional-label">
       value from <code>*name</code> column of <span class="required-excel-sheet-color">process</span> sheet
    </td>
    <td class="row-4 row-4-required-optional-label">
      equipment used in process
    </td>
    <td class="row-4 row-4-required-optional-label">
      description of the equipment
    </td>
    <td class="row-4 row-4-required-optional-label">
      value/description of condition
    </td>
    <td class="row-4 row-4-required-optional-label">
      value from <code>*name</code> column of <span class="optional-excel-sheet-color">citation</span> sheet
    </td>
  </tr>
</table>

---

<br>

<h2>
 <span class="optional-excel-sheet-color"><u>prerequisite process</u></span> 
 sheet 
 <span style="color: grey; font-size: 0.8rem;">(optional)</span>
</h2>

Define the immediate prerequisites for each process.

> e.g., Assuming `A -> B -> C`, the immediate prerequisite of `C` is `B` (not `A`).

| Row 2          | Row 1    | Required | Row 4 - ∞ expected value                     |
|----------------|----------|----------|----------------------------------------------|
| \*process      | relation | yes      | value from `*name` column of `process` sheet |
| \*prerequisite | relation | yes      | value from `*name` column of `process` sheet |

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *process
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *prerequisite
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
  </tr>
  <tr>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
  </tr>
  <tr>
    <td class="row-4 row-4-required-optional-label">
      value from *name of <span class="required-excel-sheet-color">process</span> sheet
    </td>
    <td class="row-4 row-4-required-optional-label">
      value from *name of <span class="required-excel-sheet-color">process</span> sheet
      <br> <em>immediate prerequisite step</em>
    </td>
  </tr>
</table>

---

<br>

#### <span class="required-excel-sheet-color"><u>process ingredient</u></span> sheet

<br>

> Defines the ingredients used in the process

<br>

Define the ingredients for each process and their respective quantities.

| Row 2                                                                          | Row 1     | Required | Row 4 - ∞ expected value                                                                |
|--------------------------------------------------------------------------------|-----------|----------|-----------------------------------------------------------------------------------------|
| \*process                                                                      | relation  | yes      | value from `*name` column of `process` sheet                                            |
| \*material                                                                     | relation  | yes      | value from `*name` column of `material` sheet                                           |
| \*keyword                                                                      | attribute | yes      | pick from `Name` column of [ingredients](https://criptapp.org/keys/ingredient-keyword/) |
| pick from `Name` column of [quantity](https://criptapp.org/keys/quantity-key/) | quantity  | yes      | record your quantity here                                                               |

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">quantity</u> 
    </td>
    <td class="row-1">
      <u class="row-1">quantity</u> 
    </td>
    <td class="row-1">
      <u class="row-1">quantity</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *process
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *material 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>    
    <td class="row-2">
      *keyword
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      <a href="https://criptapp.org/keys/quantity-key/" 
      target="_blank">quantity value</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      <a href="https://criptapp.org/keys/quantity-key/"
        target="_blank">quantity value</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
      <td class="row-2">
      <a href="https://criptapp.org/keys/quantity-key/"
        target="_blank">quantity value</a>
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>

  </tr>
  <tr>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3">
      <div></div>
    </th>
    <th class="row-3-in-table">
      <div>ml</div>
    </th>
    <th class="row-3-in-table">
      <div>g</div>
    </th>
    <th class="row-3-in-table">
      <div>mole</div>
    </th>
  </tr>
  <tr>
    <td class="row-4 row-4-required-optional-label">
       value comes from *name column of the <span class="required-excel-sheet-color">process</span> sheet
    </td>
    <td class="row-4 row-4-required-optional-label">
      value comes from *name column of the <span class="required-excel-sheet-color">materials</span> sheet
    </td>
    <td class="row-4 row-4-required-optional-label">
      my keyword to find this ingredient
    </td>
    <td class="row-4 row-4-required-optional-label">
      5
    </td>
    <td class="row-4 row-4-required-optional-label">
      0.455
    </td>
    <td class="row-4 row-4-required-optional-label">
      10
    </td>
  </tr>
</table>

---

<br>

#### <span class="required-excel-sheet-color"><u>process product</u></span> sheet

<br>

> This sheet describes the resulting product after completing a process

<br>

Define the material products of each process.

| Row 2      | Row 1    | Required | Row 4 - ∞ expected value                   |
|------------|----------|----------|--------------------------------------------|
| \*process  | relation | yes      | value from `*name`column of`process`sheet  |
| \*material | relation | yes      | value from`*name`column of`material` sheet |

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *process
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *material 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
  </tr>
  <tr>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
  </tr>
  <tr>
    <td class="row-4 row-4-required-optional-label">
       value comes from *name column of the <span class="required-excel-sheet-color">process</span> sheet
    </td>
    <td class="row-4 row-4-required-optional-label">
      value comes from *name column of the <span class="required-excel-sheet-color">materials</span> sheet
    </td>
  </tr>
</table>

---

<br>

#### <span class="required-excel-sheet-color"><u>data</u></span> sheet

<br>

> This sheet defines the data files you want to upload to CRIPT, such as a csv file from a robot, an image, or any other
> type of file

<br>

Define the data sets you will be associating with properties, etc.

| Row 2        | Row 1     | Required | Row 4 - ∞ expected value                                                     |
|--------------|-----------|----------|------------------------------------------------------------------------------|
| \*experiment | relation  | yes      | value from `*name`column of`experiment`sheet                                 |
| \*name       | attribute | yes      | unique name                                                                  |
| \*type       | attribute | yes      | pick from `Name` column of [data type](https://criptapp.org/keys/data-type/) |
| sample_prep  | attribute | no       | regular text                                                                 |
| citation     | relation  | no       | value from`*name`column of`citation` sheet                                   |
| notes        | attribute | no       | regular text                                                                 |

<br>

<table>
  <tr>
    <td class="row-1">
      <u class="row-1">relation</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>    
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *experiment
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *name 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *type 
      <br> <span style="font-size: 0.7rem; font-style: italic">(Required)</span>
    </td>
    <td class="row-2">
      *source 
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
  </tr>
  <tr>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
  </tr>
  <tr>
    <td class="row-4" style="font-size: 0.8rem;">
       value from *name column of <span class=".required-excel-sheet-color">experiment</span> sheet
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      Pick a unique name
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      My type
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
        <b>Can be either local:</b>
        <br>
        <em>
            C:\Users\myUsername\Desktop\MIT\cript-excel-uploader\example_template_v0-3-1.xlsx
        </em>
        <br> <br>
        <b>Or on the web: </b>
        <br>
        <em>
            https://google.com
        </em>
    </td>
  </tr>
</table>

<br>

---

<br>

#### <span class="required-excel-sheet-color"><u>citation</u></span> sheet

> This sheet can be used to reference any sources used in the experiments that you want to cite in CRIPT

<blockquote>
  <code>Row 1:</code> can only be an <em><q>attribute</q></em> <br>
  <code>Row 2:</code> MUST have a title column, but ALL other columns are optional <br>
  <code>Row 3:</code> This row is left blank
</blockquote>

<br>

Define references to be associated with properties, etc. as citations.

| Row 2     | Row 1     | Required | Row 4 - ∞ expected value |
|-----------|-----------|----------|--------------------------|
| \*title   | attribute | yes      | unique title             |
| doi       | attribute | no       | text                     |
| authors   | attribute | no       | text                     |
| journal   | attribute | no       | text                     |
| publisher | attribute | no       | text                     |
| year      | attribute | no       | number                   |
| volume    | attribute | no       | text                     |
| issue     | attribute | no       | text                     |
| pages     | attribute | no       | text                     |
| issn      | attribute | no       | text                     |
| arxiv_id  | attribute | no       | text                     |
| pmid      | attribute | no       | text                     |
| website   | attribute | no       | text                     |
| notes     | attribute | no       | text                     |

<br>

<table style="display: block; max-width: fit-content; margin: 0 auto; overflow-x: auto; white-space: nowrap;">
  <tr>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
    <td class="row-1">
      <u class="row-1">attribute</u> 
    </td>
  </tr>
  <tr>
    <td class="row-2">
      *title
      <br> <span style="font-size: 0.7rem; font-style: italic">(*Required)</span>
    </td>
    <td class="row-2">
      doi 
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      authors
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      journal
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      publisher
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      year
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      volume
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      issue
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      pages
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      issn
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      arxiv_id
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      pmid
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      website
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
    <td class="row-2">
      notes
      <br> <span style="font-size: 0.7rem; font-style: italic">(optional)</span>
    </td>
  </tr>
  <tr>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
    <th class="row-3">
      <div style="margin-bottom: 1rem;"></div>
    </th>
  </tr>
  <tr>
    <td class="row-4" style="font-size: 0.8rem;">
      Each title must be unique
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      your doi here
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      Author Here
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      Journal name
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      publisher name
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      year published
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      volume number
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      issue
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      pages
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      issn
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      arxiv_id
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      pmid
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      https://www.example.com
    </td>
    <td class="row-4" style="font-size: 0.8rem;">
      These are my notes
    </td>

  </tr>
</table>

<br><br><br>

---
