# CRIPT Excel Uploader

## Usage

### Follow these steps

<ol id="usage-steps">
  <li>
    Login or Signup for the <a href="https://www.criptapp.org/" target="_blank">CRIPT platform</a>
  </li>
  <li>
    Create a <b>Project</b> inside the 
    <a href="https://www.criptapp.org/project" target="_blank">CRIPT platform</a>
    <ul>
      <li>
        A Project can be thought of as a bunch of folders each containing experiments that contribute to a single project
      </li>
      <li>
        Essentially, the project can be thought of as a folder that holds Collection nodes
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
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.6.0/CRIPT_template.xlsx">
        CRIPT Excel Template
    </a>
    <ul>
      <li>
          The CRIPT Excel Template can be used to directly record data in the file
      </li>
      <li>
          The CRIPT Excel Template contains formulas and validations that makes recording data much easier
      </li>
      <li>
        The 
        <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.6.0/CRIPT_template.Example.xlsx">
          CRIPT <b>Example</b> Excel Template
        </a>
        can serve as an example Excel file for users to see the overall flow and structure of the Excel file
      </li>
    </ul>
  </li>
  <li>
    Download the
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.6.0/CRIPT.Excel.Uploader.exe">
      CRIPT Excel Uploader executable
    </a>
  <li>
    Input your data into the CRIPT Excel template
    <ul>
      <li>
        Refer to <a href="excel_rows" target="_blank">structure of Excel sheet</a> 
        to understand rows 1-4 of every sheet
      </li>
      <li>
        Refer to <a href="individual_sheets" target="_blank">individual sheets</a> to see the options for each sheet
      </li>
    </ul>
  </li>
  <li>
    Run CRIPT Excel Uploader
    <ul>
      <li>
        <b><em>Windows:</em></b> simply double click on the executable to run
      </li>
       <li>
        <b><em>Mac:</em></b> simply double click on the executable to run
      </li>
      <li>
        <b><em>Linux</em></b>  convert file to executable by <code>chmod +x excel_uploader_linux</code> and then run the file as usual
      </li>
    </ul>
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
