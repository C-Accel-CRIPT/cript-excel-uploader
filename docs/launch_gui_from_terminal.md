# Alternative Way to Launch the Executable

In addition to launching the graphical user interface by downloading the correct file, and running it via double click,
users can always launch the program via terminal.

You may want to run the program via terminal for several reasons.

Follow these steps to launch the program via terminal:

1. Download <a href="https://www.python.org/downloads/" target="_blank">python 3.9 or higher</a>

2. Git clone the
    <a href="https://github.com/C-Accel-CRIPT/cript-excel-uploader" target="_blank">
    master branch of the CRIPT Excel Uploader repository
    </a>

    ```bash
    git clone https://github.com/C-Accel-CRIPT/cript-excel-uploader.git
    ```

3. Navigate to the repository that was just cloned

    ```bash
    cd cript-excel-uploader
    ```

4. Create virtual environment for needed dependencies

    === ":fontawesome-brands-windows: Windows"
        ``` bash 
        python -m venv .\venv
        ```

    === ":fontawesome-brands-apple: Mac & :fontawesome-brands-linux: Linux"

        ``` bash
        python3 -m venv ./venv
        ```

5.  Activate virtual environment

    === ":fontawesome-brands-windows: Windows"

        ``` bash
        .\venv\Scripts\activate
        ```

    === ":fontawesome-brands-apple: Mac & :fontawesome-brands-linux: Linux"

        ``` bash
        source venv/bin/activate
        ```

6.  Install needed dependencies

    ```bash
    pip install -r requirements.txt
    ```

7.  Navigate to directory

    === ":fontawesome-brands-windows: Windows"

        ``` bash
        cd .\src\
        ```

    === ":fontawesome-brands-apple: Mac & :fontawesome-brands-linux: Linux"

        ``` bash
        cd src/
        ```

9.  Run the GUI

    === ":fontawesome-brands-windows: Windows"

        ``` bash
        python gui_main.py
        ```

    === ":fontawesome-brands-apple: Mac & :fontawesome-brands-linux: Linux"

        ``` bash
        python3 gui_main.py
        ```

The CRIPT Excel Uploader graphical user interface should now be running

<img 
   alt="Screenshot of CRIPT Excel Uploader GUI first screen" class="screenshot-border" style="width: 28rem;"
   src="../docs_assets/filling_out_config/cript_excel_uploader_gui_start_screen_screenshot.png">
