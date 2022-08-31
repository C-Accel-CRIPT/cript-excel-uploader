# Running CRIPT <span style="color: var(--excel-light-color)">Excel</span> Uploader

## Using the executable

**Windows**

1. Download <code>cript_uploader_vX-X-X.exe</code> from
   the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)
2. Be sure config.yaml, Excel file, and cript_uploader_vX-X-X.exe file are all in the same directory
3. Double-click on <code>cript_uploader_vX-X-X.exe</code> to run the program

<br>

[//]: # (TODO change this away from terminal and more towards clicking on GUI)
**Mac or Linux**

1. Download <code>cript_uploader_vX-X-X</code> from
   the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)
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

## Alternatively, you can run the Python Script Directly

_Basic Setup:_

1. [Download Python(>=3.10)](https://www.python.org/)

2. [Download Git](https://git-scm.com/downloads)

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
