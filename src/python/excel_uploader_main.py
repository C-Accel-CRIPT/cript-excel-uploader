import cript
import globus_sdk

from python import create
from python import parse
from python import upload
from python.create import error_list as create_error_list
from python.sheet_parameters import sheet_parameters


class ExcelUploader:
    def __init__(self):
        self.api = None
        self.project_object = None
        self.collection_object = None
        self.data_is_public = False

        # used in create nodes function
        self.nodes = {}

        # globus resources
        self.globus_auth_link = None
        self.has_authenticated_with_globus = False

        # after successful upload we have a collections URL
        self.collection_url = None

        # keeps the current progress of upload.py to update on the gui
        self.current_progress = 0
        self.total_progress_needed = 0

        # holds any errors that could come up during upload_driver
        self.error_list = []

    def authenticate_user(self, host, api_token):
        """
        This method is just called to create an api and authenticate the user.
        If host or token is wrong, then it raises and error and the method calling it
        will know that authentication failed, and there is no api endpoint created yet
        :param host: string
        :param api_token: string
        :return: None
        :raises: cript.exceptions.APIAuthError, requests.exceptions.RequestException
        """
        self.api = cript.API(host, api_token)

        # globus authentication is false on every new connection
        self.has_authenticated_with_globus = False

    def set_project(self, project_name):
        """
        Is called with project_name
        gets the project object from cript and sets the class variable.
        If it raises an exception, then that tells the function calling it that this project_object
        does not exist within cript
        :param project_name: string
        :return: None
        :raises: cript.exceptions.APIGetError
        """
        self.project_object = self.api.get(cript.Project, {"name": project_name})

    def set_collection(self, collection_name):
        """
        Is called with collection_name
        gets the collection object from cript and sets the class variable.
        If it raises an exception, then that tells the function calling it that this collection_object
        does not exist within cript
        :param collection_name: string
        :return: None
        :raises: cript.exceptions.APIGetError
        """
        self.collection_object = self.api.get(cript.Collection, {"name": collection_name})

    def is_uploading_local_files(self, files):
        """
         method checks if there are any files to upload first
         if there are files to upload then it loops through and checks the source of each file node
         if a single source does not have http:// or https:// then it returns true and user needs
         to go to Globus auth screen
         if loop completes and all the sources are have web indications (http or https) then
         user is uploading all web files, doesn't need to authenticate with globus, and returns False

        :params files: files is an array of file nodes
        :returns: True if use has local files to upload,
        and False if user does not have any files to upload or the files they want to upload are all on the web
        """

        if len(files) < 1:
            return False

        for key in files:
            # if file is local
            if ("http://" not in files[key].source) and ("https://" not in files[key].source):
                return True

        return False

    def set_globus_auth_link(self):
        """
         sets the url for globus auth, that then can be accessed and given to the frontend
         for the user to click and get their auth token from globus
        :returns: None
        """
        self.globus_auth_link = self.api.storage_client.get_authorize_url()

    def is_globus_auth_token_valid(self, globus_auth_token):
        """
         trys to authenticate the user with the link and token

         if authentication is successful then it sets that user has authenticated
         with globus successfully as True

         if authentication fails, then it sets it as false and returns false

         this method is both a getter and a setter, which is bad design and needs to be improved
         later

        :param globus_auth_token: str globus auth token/code inputted by the user
        :returns: True if tokens were valid and False if it was invalid
        """
        # TODO consider passing in globus auth link, and token to the whole function
        try:
            self.api.storage_client.set_tokens(self.globus_auth_link, globus_auth_token)

        # TODO later needs to catch error from other storage clients too
        except globus_sdk.services.auth.errors.AuthAPIError:
            self.has_authenticated_with_globus = False
            return self.has_authenticated_with_globus

        # if authentication is successful, record that user authenticated and
        self.has_authenticated_with_globus = True
        return self.has_authenticated_with_globus

    def get_total_for_progress_bar(self, nodes_list):
        """
        loop through the list of nodes and add up all their lengths
        for total for progress bar.
        e.g. total = len(materials) + len(experiments) + len(data) ...
        return total
        :param: nodes_list: list of nodes that will be passed to upload
        :return: None
        """

        total = 0

        for node in nodes_list:
            total += len(node)

        # TODO I am 3 over for the total
        return total - 3

    def upload_driver(self, excel_file_path, data_is_public, gui_object):
        """
        The driver method that calls all the other methods to upload everything
        parses the Excel sheets, and if any errors then give them to gui_object.display_errors
        If error_list is 0, then parsing was successful, then we can upload to cript
        after uploading get the collections URL in CRIPT, and send it to gui_object.display_success
        to show the user where their data is stored within cript
        :param excel_file_path: string
        :param data_is_public: boolean
        :param gui_object: eel_GUI object
        :returns: a list of errors that gui_object can see if there were any errors in the process and send
                 them to error screen or if there were no errors to send them to globus screen
        """

        parsed_sheets = {}
        for parameter in sheet_parameters:
            # Creates a Sheet object to be parsed for each sheet
            parsed_sheets[parameter["name"]] = parse.Sheet(
                excel_file_path,
                parameter["name"],
                parameter["required_columns"],
                unique_columns=parameter["unique_columns"],
            ).parse()

        ###
        # Create and validate
        ###

        experiments = create.create_experiments(parsed_sheets["experiment"], self.collection_object, data_is_public)
        references, citations = create.create_citations(
            parsed_sheets["citation"], self.project_object.group, data_is_public
        )
        data, files = create.create_data(
            parsed_sheets["data"], self.project_object, experiments, citations, data_is_public
        )
        materials = create.create_materials(
            parsed_sheets["material"], self.project_object, data, citations, data_is_public
        )
        materials = create.create_mixtures(parsed_sheets["mixture component"], materials)
        processes = create.create_processes(
            parsed_sheets["process"], experiments, data, citations, data_is_public
        )

        # if there is local files to upload, and they have not authenticated with storage client yet
        # take them to authenticate with globus
        # TODO need to check if the file node exists first and then check if there is any
        if self.is_uploading_local_files(files) and not self.has_authenticated_with_globus:
            # take them to globus screen
            self.set_globus_auth_link()
            gui_object.globus_auth(self.globus_auth_link)
            return

        # create
        create.create_prerequisites(parsed_sheets["prerequisite process"], processes)
        create.create_ingredients(parsed_sheets["process ingredient"], processes, materials)
        create.create_products(parsed_sheets["process product"], processes, materials)
        create.create_equipment(parsed_sheets["process equipment"], processes, data, citations)

        # any error coming from create has now been recorded here in case anything else wants to know
        # if there were any errors or not
        self.error_list = create_error_list

        if self.error_list:
            gui_object.display_errors(self.error_list)
            return self.error_list

        # files and citations are not being used
        nodes_list = [experiments, references, citations, data, files, materials, processes]
        self.total_progress_needed = self.get_total_for_progress_bar(nodes_list)

        ###
        # Upload
        ###

        upload.upload(
            self.api, files, "File", self, gui_object
        )

        upload.upload(
            self.api, experiments, "Experiment", self, gui_object
        )

        upload.upload(
            self.api, references, "Reference", self, gui_object
        )

        upload.upload(
            self.api, data, "Data", self, gui_object
        )

        upload.upload(
            self.api, materials, "Material", self, gui_object
        )

        upload.upload(
            self.api, processes, "Process", self, gui_object
        )

        # TODO what is going on here?
        # TODO arguments should be in the same order as others
        upload.add_sample_preparation_to_process(
            parsed_sheets["data"], data, processes, self.api, self, gui_object
        )

        return self.error_list

    def get_collections_url(self):
        """
        gets the collection object url after it has been successfully
        uploaded to CRIPT so users can see their data in CRIPT

        :returns: str: which is a url for CRIPT collection
        """
        return self.collection_object.url.replace("api/", "")
