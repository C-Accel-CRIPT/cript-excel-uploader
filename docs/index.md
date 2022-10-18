# CRIPT Excel Uploader

## Usage

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
        A Project can be thought of as a bunch of folders each containing experiments that contribute to a single project
      </li>
      <li>
        Essentially, the project can be thought of as Collections put inside of one folder
      </li>
      <li>
        A Project is needed because each Collection belongs inside of a Project
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
    Download the 
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/example_template_v0-4-2.xlsx">
        example_template_vX-X-X.xlsx
    </a>
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
    Download the
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/config.yaml">
          config.yaml
    </a>
    <ul>
      <li>
        <a href="filling_out_config" target="_blank">Fill out template with your information</a>
      </li>
    </ul>
  </li>

  <li>
  <!-- TODO be sure to keep this version up to date -->
    Download the
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/main.exe">
      executable
    </a>
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
    Input your data into the excel sheet
    <ul>
      <li>
        Refer to <a href="filling_out_config" target="_blank">filling out row 1 - 3</a> to understand the Excel file
        structure
      </li>
      <li>
        Refer to <a href="individual_sheets" target="_blank">individual sheets</a> to see what is allowed in each sheet
      </li>
    </ul>
  </li>
  <li>
    <a href="how_to_run_excel_uploader" target="_blank">
      Run CRIPT Excel Uploader
    </a>
  </li>
</ol>

---

## FAQ

- **_What happens if I run the uploader more than once?_**  
  If the name of an object has not been changed, the existing object will be updated in the database. If the name has
  been changed, a new object will be created and the old will remain.

- **_I entered a number into a cell but the uploader says the value is a string. What gives?_**  
  This is likely caused by the wrong value type being set for the given cell in the Excel document.

- **_What units can I use?_**  
  Here is a list of the <a href="https://github.com/hgrecco/pint/blob/master/pint/default_en.txt" target="_blank">
  supported units</a>
  from the Pint Python package.

- **_What if I have multiple measurements of the same thing?_**  
  You can use an `ID` field in front of row 2 to separate out the different measurements more on that in
  the <a href="excel_rows/#id-optional" target="_blank">ID section of Row 2</a>

<div style="margin-bottom: 5rem;"></div>
