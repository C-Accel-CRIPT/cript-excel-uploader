# native imports
import sys
import tkinter
import traceback
from tkinter import filedialog

# third party imports
import cript
import eel
import requests

# my imports
# TODO this needs to change after alternative main is renamed to something like Driver
from excel_uploader_main import ExcelUploader
from create import error_list as create_error_list


class ExcelUploaderGUI:
    def __init__(self):
        # initialize eel
        self.eel = eel
        self.eel.init("../web")

        self.host = None
        self.api_key = None
        self.project_name = None
        self.collection_name = None
        self.data_is_public = False
        self.excel_file_path = None

        self.excel_uploader = ExcelUploader()

    def start_app(self):
        """
        starts the app
        :return: none
        """
        self.eel.start(
            'templates/base.html',
            jinja_templates='templates',
            size=(800, 850),
        )

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
        :return: none
        """
        root = tkinter.Tk()
        # root.iconbitmap("./assets/logo_condensed.ico")
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        # allows only Excel files to be selected
        path_to_excel_file = filedialog.askopenfilename(title="Select your CRIPT Excel file",
                                                        filetypes=(
                                                            ("Excel file", "*.xlsx"),
                                                        )
                                                        )
        eel.setExcelFilePath(path_to_excel_file)

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

        self.data_is_public = user_input["isDataPublic"]

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

        # at the end it returns an error list that I can check for errors
        error_list = self.excel_uploader.upload_driver(self.excel_file_path, self.data_is_public, self)

        if len(error_list) > 0:
            print("hit error list")
            self.display_errors(error_list)
            return
        else:
            print("hit continue to globus clause")
            self.globus_auth("https://google.com")
            return

    def globus_auth(self, globus_auth_link):
        """
        this function is called when globus authentication is needed
        changes the screen to globus auth screen, and sends the globus_auth_link
        to JS to set it in dom, so user can click on and get their token

        :params: globus_auth_link: str, that is a link to globus auth
        """

        print("taking user to globus screen")
        # after upload go to globus for authentication
        eel.goToGlobusAuthScreen()

        # set globus auth link for html <a href=""
        eel.setGlobusAuthlink(globus_auth_link)

        # get globus auth link from sdk
        # after sdk says theyve been authenticated then send them to success screen

    # JS calls this
    def globus_auth_token_validation(self, globus_auth_token):
        """
        JS calls this function when the user submits the globus auth token.
        this function checks the token, and if everything is valid,
        then it sends them to the success screen

        :params: globus_auth_token: str, globus auth token e.g. "OtJKBk25bjHg1KbcwW50eCKx402G2x"
        :returns: True or False, whether they authenticated or not
        """
        print(globus_auth_token)

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

        print("hit display errors")

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
    def user_closed_app(self):
        """
        If the user closes the GUI window then the program will call this method
        and the program will exit and not continue to run in the background without
        any indication.
        This method handles any clean up before exit and then exits the program nicely

        :returns: None
        """
        print("user closed the app")
        sys.exit()


if __name__ == "__main__":
    app = ExcelUploaderGUI()
    eel.expose(app.get_excel_file_path)
    eel.expose(app.validate_and_set_user_input)
    eel.expose(app.cancel_upload)
    eel.expose(app.globus_auth_token_validation)
    eel.expose(app.user_closed_app)
    app.start_app()
