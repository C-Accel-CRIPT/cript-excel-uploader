# Running CRIPT <span style="color: var(--excel-light-color)">Excel</span> Uploader

## Using the executable <code>cript_uploader</code>

- **Windows**

  - Download <code>cript_uploader_vX-X-X.exe</code> from
    the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)
  - Open a terminal and navigate the relevant folder
    ```bash
    cd <path_to_folder>
    ```
  - Run it
    ` bash .\cript_uploader_vX-X-X.exe`

<br>

- **Mac or Linux**
  - Download <code>cript_uploader_vX-X-X</code> from
    the [latest release](https://github.com/C-Accel-CRIPT/cript-excel-uploader/releases)
  - Open a terminal and navigate the relevant folder
    ```bash
    cd <path_to_folder>
    ```
  - Change the file permissions
    ```bash
    chmod 755 ./cript_uploader
    ```
  - Run it
    ```bash
    ./cript_uploader_vX-X-X
    ```

<br>

## <u>Alternatively, you can run the Python Script:</u>

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
