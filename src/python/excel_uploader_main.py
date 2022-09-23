import cript

import create
import parse
import upload
from create import error_list as create_error_list
from sheet_parameters import sheet_parameters


class ExcelUploader:
    def __init__(self):
        self.api = None
        self.project_object = None
        self.collection_object = None
        self.data_is_public = False

        # used in create nodes function
        self.nodes = {}

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

        return total

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

        # create
        create.create_prerequisites(parsed_sheets["prerequisite process"], processes)
        create.create_ingredients(parsed_sheets["process ingredient"], processes, materials)
        create.create_products(parsed_sheets["process product"], processes, materials)
        create.create_equipment(parsed_sheets["process equipment"], processes, data, citations)

        nodes_list = [experiments, references, files, materials, processes]
        self.total_progress_needed = self.get_total_for_progress_bar(nodes_list)

        # any error coming from create has now been recorded here in case anything else wants to know
        # if there were any errors or not
        self.error_list = create_error_list

        if self.error_list:
            gui_object.display_errors(self.error_list)
            return self.error_list

        ###
        # Upload
        ###

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

        upload.upload(
            self.api, files, "File", self, gui_object
        )

        # TODO what is going on here?
        upload.add_sample_preparation_to_process(
            parsed_sheets["data"], data, processes, self.api, self, gui_object
        )

        return self.error_list

    def get_collections_url(self):
        """
        gets the collection object url after it has been uploaded to CRIPT
        so users can see their data in CRIPT

        :returns: str: which is a url for CRIPT collection
        """
        return self.collection_object.url.replace("api/", "")
