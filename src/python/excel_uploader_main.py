import cript

import create, parse, upload
from create import error_list
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

    def get_parsed_sheets(self, excel_file_path):
        """
        parses sheets and returns it to be used by create_nodes()
        :param excel_file_path:
        :return: dict
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

        return parsed_sheets

    # TODO this function isn't made the best, and should be refactored after tested and it works
    def create_nodes(self, parsed_sheets, data_is_public):
        """

        :param parsed_sheets:
        :param data_is_public:
        :return: error_list
        """
        self.nodes["experiments"] = create.create_experiments(
            parsed_sheets["experiment"], self.collection_object, data_is_public)
        self.nodes["references"], self.nodes["citations"] = create.create_citations(
            parsed_sheets["citation"], self.project_object.group, data_is_public
        )
        self.nodes["data"], self.nodes["files"] = create.create_data(
            parsed_sheets["data"], self.project_object, self.nodes["experiments"], self.nodes["citations"],
            data_is_public
        )
        self.nodes["materials"] = create.create_materials(
            parsed_sheets["material"], self.project_object, self.nodes["data"], self.nodes["citations"],
            data_is_public
        )
        self.nodes["materials"] = create.create_mixtures(
            parsed_sheets["mixture component"], self.nodes["materials"]
        )
        self.nodes["processes"] = create.create_processes(
            parsed_sheets["process"], self.nodes["experiments"], self.nodes["data"],
            self.nodes["citations"],
            data_is_public
        )

        create.create_prerequisites(parsed_sheets["prerequisite process"], self.nodes["processes"])
        create.create_ingredients(
            parsed_sheets["process ingredient"], self.nodes["processes"], self.nodes["materials"]
        )
        create.create_products(
            parsed_sheets["process product"], self.nodes["processes"], self.nodes["materials"]
        )
        create.create_equipment(
            parsed_sheets["process equipment"], self.nodes["processes"], self.nodes["data"],
            self.nodes["citations"]
        )

        return error_list

    def upload_to_cript(self, parsed_sheets, gui_object):
        """
        
        :param parsed_sheets: dict
        :param gui_object: passes instance of ExcelUploaderGUI to upload.py
        to update the progress bar on every loop
        :return: None
        """
        upload.upload(self.api, self.nodes["experiments"], "Experiment", gui_object)
        upload.upload(self.api, self.nodes["references"], "Reference", gui_object)
        upload.upload(self.api, self.nodes["data"], "Data", gui_object)
        upload.upload(self.api, self.nodes["materials"], "Material", gui_object)
        upload.upload(self.api, self.nodes["processes"], "Process", gui_object)
        upload.upload(self.api, self.nodes["files"], "File", gui_object)
        upload.add_sample_preparation_to_process(
            parsed_sheets["data"], self.nodes["data"], self.nodes["processes"], self.api
        )

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
        :return: None
        """
        parsed_sheets = self.get_parsed_sheets(excel_file_path)
        self.create_nodes(parsed_sheets, data_is_public)

        if len(error_list) > 0:
            gui_object.display_errors(error_list)
        else:
            self.upload_to_cript(parsed_sheets, gui_object)
            self.collection_url = self.collection_object.url.replace("api/", "")
            gui_object.display_success(self.collection_url)
