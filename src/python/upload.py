import math

import cript
from tqdm import tqdm


def upload(api, obj_dict, obj_type, current_progress, total, gui_object):
    """
    Loops through all objects and saves/updates in cript database
    at the end of every loop it calls GUI to update the progressbar
    api-obj, api connection
    obj_dict-dict, full of cript objects
    obj_type-str, describes object types being saved
    returns-None
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

        api.save(obj, update_existing=True)
        pbar.update(1)  # Increment progress bar

        # take current progress and divide it by total needed progress to get a decimal
        # multiply decimal by 100 to have percentage
        # math.floor percentage, so it's always a whole number
        progress_percentage = (current_progress/total) * 100
        progress_percentage = math.floor(progress_percentage)
        gui_object.update_progress_bar(progress_percentage, obj_type)

    pbar.close()


    return current_progress


def add_sample_preparation_to_process(parsed_data, data, processes, api):
    """Adds Process Nodes to a Data nodes "sample_preparation" field if applicable and saves updated node.
    parsed_data-dict
    data-dict of CRIPT Data objects
    processes-dict of CRIPT Process objects
    """
    for key, parsed_datum in parsed_data.items():
        parsed_cell = parsed_datum.get("sample_preparation")
        if parsed_cell is not None:
            data_node = data[key]
            process_node = processes[parsed_cell["value"]]
            data_node.sample_preparation = process_node
            # Save process with error checking
            api.save(data_node, update_existing=True)
