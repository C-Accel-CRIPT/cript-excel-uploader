import math
import time
import traceback

import cript


def update_progress_bar(obj_type, excel_uploader_object, gui_object):
    """
    This function sets the progress for the progress bar in the loading screen
    and is used in the upload function in upload.py

    It works by taking the current_progress stored in excel_uploader_object and adding 1 to it
    every time its called. Then, it divides the current_progress
    by the total_progress_needed (max times this method will be called)
    to get a ratio. Then the ratio will be floored to always get a whole number for the progress bar
    and to never get a 75.2% progress

    :params obj_type: what node we are saving, eg. "Material", "Experiment", "Mixture", etc.
    :params excel_uploader_object: excel_uploader_main.py object used to keep track of the update
    :params gui_object: gui_main.py object used to update the progress bar in the frontend
    returns: None
    """
    excel_uploader_object.current_progress += 1

    progress_percentage = (
        excel_uploader_object.current_progress
        / excel_uploader_object.total_progress_needed
    )
    progress_percentage = progress_percentage * 100
    progress_percentage = math.floor(progress_percentage)

    gui_object.update_progress_bar(progress_percentage, obj_type)
    return


def upload(obj_dict, obj_type, excel_uploader_object, gui_object):
    """
    Loops through all objects and saves/updates them in cript database
    at the end of every loop it calls gui_object.update_progress_bar()
    to update the progress bar or gui_object.display_error() to show errors to users

    :params obj_dict: dict, full of cript objects
    :params  obj_type: str, describes object types being saved e.g. "Material", "Experiment", "Data", etc.
    :params gui_object: gui_main object that allows this function to use it to call
                        gui_object.update_progress_bar()
                        or if there are any errors to call
                        gui_object.display_errors(["errors", "more errors"]) with a list of errors
                        to display to the user
    :returns: if there are any errors, it returns nothing, and instead calls gui_object.display_errors()
              If the upload loop runs successfully then it returns the current_progress at the end
    """

    for key, obj in obj_dict.items():

        try:
            if obj_type == "File" and obj.name is None:
                obj.name = obj.source

            obj.save(update_existing=True)

            # update progress bar regardless of what happens
            update_progress_bar(obj_type, excel_uploader_object, gui_object)

            # sleeps the program for 5 ms between uploads
            time.sleep(5 / 1000)

        # if Reference node already exists and user is trying to save duplicate,
        # then recognize that, do nothing, and just continue with everything else
        except cript.data_model.exceptions.UniqueNodeError as error:
            if obj_type == "Reference":
                continue
            else:
                raise error

        # TODO this needs specific errors instead of a catch all
        except Exception as error:
            # put error name into the errors and another error with the traceback
            excel_uploader_object.error_list.append(f"Error: {error}")
            excel_uploader_object.error_list.append(traceback.format_exc())

            return


def add_sample_preparation_to_process(
    parsed_data, data, processes, api, excel_uploader_object, gui_object
):
    """
    Adds Process Nodes to a Data nodes "sample_preparation" field if applicable and saves updated node.
     :params parsed_data: dict
     :params data: dict of CRIPT Data objects
     :params processes: dict of CRIPT Process objects
     :params api: api connection object
     :returns: None
    """
    for key, parsed_datum in parsed_data.items():
        parsed_cell = parsed_datum.get("sample_preparation")
        if parsed_cell is not None:
            data_node = data[key]
            process_node = processes[parsed_cell["value"]]
            data_node.sample_preparation = process_node
            # Save process with error checking
            # TODO for newest SDK changed here
            data_node.save(update_existing=True)

            # api.save(data_node, update_existing=True)
