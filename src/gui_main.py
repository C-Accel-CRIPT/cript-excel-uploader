import atexit
import os
import sys
import tkinter
from tkinter import filedialog

import cript
import eel
import requests

from python.excel_uploader_main import ExcelUploader


class ExcelUploaderGUI:
    def __init__(self):
        # user input variables needed for Excel Uploader
        self.excel_file_path = None

        # creating an instance of ExcelUploader
        self.excel_uploader = ExcelUploader()

        # initialize eel
        eel.init("web")

    def start_app(self):
        """
        starts the app
        :return: none
        """

        # cd into templates/base.html to get html path
        html_path = os.path.join("templates", "base.html")

        eel.start(html_path, size=(800, 850), port=8001)

    # JS calls this
    def get_excel_file_path(self):
        """
        this function opens a tkinter dialog box to browse to the Excel file,
        saves the path to path_to_excel_file: string, then displays that on the dom
        the string from the dom later gets submitted

        tkinter is needed to open the dialog box because browser will not share the Excel file path
        with JS, so we have no access to it, and we can't send it to python from JS either
        thus we are left with opening our own dialog box, getting the path,
        and then reading the file from absolute path

        in this method python also notifies JS when a dialog box has been opened and closed, so the user
        does not accidentally launch 100 instances of tkinter dialog box

        :return: none
        """

        # tell JS that tkinter dialog box has been opened
        eel.setIsDialogBoxOpen(True)

        root = tkinter.Tk()

        # remove the tkinter window, so we can just see the dialog box
        root.withdraw()

        root.wm_attributes("-topmost", 1)
        # allows only Excel files to be selected
        path_to_excel_file = filedialog.askopenfilename(
            title="Select your CRIPT Excel file", filetypes=(("Excel file", "*.xlsx"),)
        )

        # tell JS what the path is from tkinter dialog box
        eel.setExcelFilePath(path_to_excel_file)

        # notify js that dialog box is closed
        eel.setIsDialogBoxOpen(False)

    # JS calls this
    def validate_and_set_user_input(self, user_input):
        """
        when the user submits the start_screen.html form it comes here with all their input as a dict
        then it runs through a bunch of validations to both set the objects needed for uploading in
        excel_uploader and if the object gives an error then I catch all errors inside and put it
        inside a dict and sends that to displayFormErrors(errors) to display
        to user as an invalid input with good feedback.

        I am putting feedback as a value with the key in the dict,
        but not currently using it, however, the functionality exists if needed

        if the len of error_dict is 0 then everything is valid,
        and send_to_upload
        :param user_input: dict
        :return: None
        """

        # used to capture the validation errors to send to JS to display
        error_dict = {}

        try:
            self.excel_uploader.authenticate_user(
                user_input["host"], user_input["apiToken"]
            )

        except (cript.exceptions.APIAuthError, requests.exceptions.RequestException):
            # send JSON to JS function with fields that have errors and give feedback
            error_dict["host"] = "invalid host or token"
            error_dict["apiToken"] = "invalid host or token"

            eel.displayFormErrors(error_dict)
            return

        try:
            self.excel_uploader.set_project(user_input["projectName"])

        except cript.exceptions.APIGetError:
            error_dict["project"] = "Please enter a valid Project name"

        try:
            self.excel_uploader.set_collection(user_input["collectionName"])

        except cript.exceptions.APIGetError:
            error_dict["collection"] = "Please enter a valid Collection name"

        try:
            # just check to see if the Excel file exists,
            # if exists file then set object variable path, if not then give an error
            excel_file = open(user_input["excelFile"], "r")
            excel_file.close()
            self.excel_file_path = user_input["excelFile"]

        except FileNotFoundError:
            error_dict["excel_file"] = "Excel file not found"

        # if no errors then everything is set and take them to loading screen
        if len(error_dict) == 0:
            self.send_to_upload()

        # if errors then display them to the user with feedback
        else:
            eel.displayFormErrors(error_dict)

    def send_to_upload(self):
        """
        After validate_and_set_user_input() passes, then it calls this function to
        change the screen from start_screen.html to loading_screen.html
        all excel_uploader required objects get sent and upload_driver starts to work
        and there the upload.py starts to increment the progress bar as it uploads
        :return: None
        """
        eel.goToLoadingScreen()

        # public data is not allowed from Excel Uploader
        data_is_public = False

        # at the end it returns an error list that I can check for errors
        error_list = self.excel_uploader.upload_driver(self.excel_file_path, self)

        # TODO this throws TypeError: object of type 'NoneType' has no len() when taking to globus
        #   screen and not returning any errors
        if len(error_list) > 0:
            print("hit error list")
            self.display_errors(error_list)
            return
        else:
            self.display_success(self.excel_uploader.get_collections_url())
            return

    def globus_auth(self, globus_auth_link):
        """
        this function is called when globus authentication is needed
        changes the screen to globus auth screen, and sends the globus_auth_link
        to JS to set it in dom, so user can click on and get their token

        :params: globus_auth_link: str, that is a link to globus auth
        """

        # after upload go to globus for authentication
        eel.goToGlobusAuthScreen()

        # set globus auth link for html <a href=""
        eel.setGlobusAuthlink(globus_auth_link)

        # get globus auth link from sdk
        # after sdk says theyve been authenticated then send them to success screen

    # JS calls this
    def globus_auth_token_validation(self, globus_auth_token):
        """
        JS calls this method when the user submits the globus auth token.
        this function sends the token to excel_uploader_main.py where it
        validates it and returns a true or false for validation.

        This method will then either show invalid feedback error to user or continue
        the upload process

        :params: globus_auth_token: str, globus auth token e.g. "OtJKBk25bjHg1KbcwW50eCKx402G2x"
        :returns: True or False, whether they authenticated or not
        """

        globus_token_is_valid = self.excel_uploader.is_globus_auth_token_valid(
            globus_auth_token
        )

        # globus token is valid, take them to upload again
        if globus_token_is_valid:
            self.send_to_upload()

        # token is invalid, show feedback on UI, and ask for token again
        else:
            eel.invalidGlobusAuthToken()

    # JS calls this
    def cancel_upload(self):
        """
        when cancel button is clicked on the frontend it shows the progress bar is canceled, waits a
        second, and closes the window, then it fires this function to just exit the whole program

        must be exposed for JS to call it

        :return: None
        """
        print("user canceled the upload")
        sys.exit()

    # this calls JS
    def update_progress_bar(self, progress_number, progress_label):
        """
        gets called on every loop iteration from ../excel_uploader/upload.py
        and the number is calculated by (iteration number/ dictionary length) * 100
        and then floor that to get the nearest whole number,
        so we don't end up with 75.2%

        then the progress_number is passed to updateLoadingBar to change the percent completed
        and progress_label says what is being is currently being uploaded e.g. "uploading material"

        this function then calls the JS function updateLoadingBar to update it on the dom

        :param: progress_label: str label for frontend of what is being uploaded "uploading materials"
        :param: progress_number: int
        :return: none
        """
        eel.updateLoadingBar(progress_number, progress_label)

    # this calls JS
    def display_errors(self, error_list):
        """
        gets called by ../excel_uploader/excel_uploader_main.py from upload_driver() when there is an error
        the error_list comes into here then gets sent to JS addErrorsToScreen(errorList) to loop through and add to dom
        :param error_list: list
        :return: None
        """

        eel.goToErrorScreen()
        eel.addErrorsToScreen(error_list)
        return

    # this calls JS
    def display_success(self, collection_url):
        """
        navigates user to the success screen and then fires JS function of
        displayCollectionURL(collection_url) and attaches collection_url to dom
        :param collection_url: string
        :return: None
        """
        eel.goToSuccessScreen()
        eel.displayCollectionURL(collection_url)

    # JS calls this
    def reset_for_uploading(self):
        """
        this method is called by JS when the user reaches the error screen and
        clicks on the "Try again" button to clear out the errors that were placed in the
        error_list that may have already contained error, so we do not just keep adding on to it
        also, the count for the progress bar needs to be reset to 0 so it does not start from 100
        """
        self.excel_uploader.error_list.clear()
        self.excel_uploader.reset_progress()
        return

    # JS calls this
    def user_closed_app(self):
        """
        If the user closes the GUI window then the program will call this method
        and the program will exit and not continue to run in the background without
        any indication.
        This method handles any clean up before exit and then exits the program nicely

        :returns: None
        """
        print("user closed the app")

        # stop the program
        sys.exit()

    # this calls JS
    def program_exit_clean_up(self):
        """
        This method is called when python is about to exit the program
        either because of an exception or whatever else.
        It is meant to be used to clean up whatever python was doing
        and then close the GUI to let the user know the program has ended
        returns: None
        """
        print("python exited the program and GUI is being closed")

        # tells JS frontend to clean up and close the GUI, as the python program has exited
        eel.pythonExitCleanUp()
        return


if __name__ == "__main__":
    app = ExcelUploaderGUI()

    # functions that JS can call
    eel.expose(app.get_excel_file_path)
    eel.expose(app.validate_and_set_user_input)
    eel.expose(app.cancel_upload)
    eel.expose(app.globus_auth_token_validation)
    eel.expose(app.reset_for_uploading)
    eel.expose(app.user_closed_app)

    # start the app
    app.start_app()

    # register method to handle clean up when python exits
    atexit.register(app.program_exit_clean_up)
