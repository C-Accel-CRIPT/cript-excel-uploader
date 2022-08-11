import cript
from tqdm import tqdm


def upload(api, obj_dict, obj_type):
    """Saves/updates objects to cript database.
    api-obj, api connection
    obj_dict-dict, full of cript objects
    obj_type-str, describes object types being saved
    returns-None"""

    # Instantiate progress bar
    pbar = tqdm(
        total=len(obj_dict),
        mininterval=0.1,
        dynamic_ncols=True,
        desc=f"Uploading {obj_type} objects: ",
        unit="item",
    )
    for key, obj in obj_dict.items():
        api.save(obj, update_existing=True)
        pbar.update(1)  # Increment progress bar

    pbar.close()


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
