import math
import traceback

import cript
from tqdm import tqdm


def upload(api, obj_dict, obj_type, current_progress, total, gui_object):
    """
    Loops through all objects and saves/updates them in cript database
    at the end of every loop it calls gui_object.update_progress_bar()
    to update the progress bar or gui_object.display_error() to show errors to users

    :params api: api connection object
    :params obj_dict: dict, full of cript objects
    :params  obj_type: str, describes object types being saved e.g. "Material", "Experiment", "Data", etc.
    :params current_progress: int, current_progress is kept by excel_uploader_main.py
                               and is passed to this function so this function can increment correctly on
                               every loop and update progressbar in the gui far,
                               gui_object.update_progress_bar()
    :params total: int, the total amount of loops needed to upload everything
                   total is used to (current_progress / total) to get the decimal amount of progress that
                   has been made on the upload, then multiply by 100, to get percentage
                   then floor the number to only get ints in the progress bar
    :params gui_object: gui_main object that allows this function to use it to call
                        gui_object.update_progress_bar()
                        or if there are any errors to call
                        gui_object.display_errors(["errors", "more errors"]) with a list of errors
                        to display to the user
    :returns: if there are any errors, it returns nothing, and instead calls gui_object.display_errors()
              If the upload loop runs successfully then it returns the current_progress at the end
    """

    # Instantiate progress bar
    pbar = tqdm(
        total=len(obj_dict),
        mininterval=0.1,
        dynamic_ncols=True,
        desc=f"Uploading {obj_type} objects: ",
        unit="item",
    )

    for key, obj in obj_dict.items():
        # increment progress wherever it was
        current_progress += 1

        try:
            api.save(obj, update_existing=True)

        except cript.exceptions.APISaveError as error:
            # put error name into the errors and another error with the traceback
            print("hit cript.exceptions.APISaveError")
            errors = [f"cript.exceptions.APISaveError: {error}", traceback.format_exc()]
            gui_object.display_error()
            return

        pbar.update(1)  # Increment progress bar

        progress_percentage = (current_progress / total) * 100
        progress_percentage = math.floor(progress_percentage)
        gui_object.update_progress_bar(progress_percentage, obj_type)

    pbar.close()

    return current_progress


def add_sample_preparation_to_process(parsed_data, data, processes, api, gui_object):
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
            api.save(data_node, update_existing=True)
