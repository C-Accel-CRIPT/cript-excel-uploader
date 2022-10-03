# Running CRIPT <span style="color: var(--excel-light-color)">Excel</span> Uploader

## Using the executable

**Windows**

1. Download the
   <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/main.exe">
   executable
   </a>
2. Be sure the <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/config.yaml">
   config.yaml
   </a>, <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/example_template_v0-4-2.xlsx">
   example_template_vX-X-X.xlsx
   </a>, and <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/main.exe">
   cript_uploader_vX-X-X.exe
   </a>
   file are all in the same directory

3. Double-click on <code>cript_uploader_vX-X-X.exe</code> to run the program

<br>

[//]: # "TODO change this away from terminal and more towards clicking on GUI"

**Mac or Linux**

1. Download the
   <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases/download/v0.4.2/main.exe">
   executable
   </a>
2. Open a terminal and navigate the relevant folder
   ```bash
   cd <path_to_folder>
   ```
3. Change the file permissions
   ```bash
   chmod 755 ./cript_uploader
   ```
4. Run it
   ```bash
   ./cript_uploader_vX-X-X
   ```

<br>

---

## Alternatively, you can run the Python Script Directly

_Basic Setup:_

1. <a href="https://www.python.org/downloads/" target="_blank">Download Python(>=3.10)</a>

2. <a href="https://git-scm.com/downloads" target="_blank">Download Git</a>

3. Open a terminal

4. Install virtualenv

   ```bash
   pip install virtualenv
   ```

5. Create a virtual environment

   ```bash
   python3 -m virtualenv ./cript-uploader
   ```

6. Activate the virtual environment  
   **_Windows_**:

   ```bash
   cript-uploader\Scripts\activate
   ```

   **_Mac or Linux_**:

   ```bash
   source cript-uploader\bin\activate
   ```

7. Clone the repository

   ```bash
   git clone git@github.com:C-Accel-CRIPT/cript-excel-uploader.git
   ```

8. Change to the project directory

   ```bash
   cd cript-excel-uploader
   ```

9. Download requirements

   ```bash
   pip install -r requirements.txt
   ```

10. Run the **main.py** file
    ```bash
    python main.py
    ```

<br>
