import time
import os
import traceback

import cript as C
from config import BASE_URL
from errors import GroupRelatedError
from util import process_track


def connect(token):
    """
    connect with backend service

    :return: backend service connection object
    :rtype: class:`cript.API`
    """
    return C.API(BASE_URL, token)


def upload_group(api, group_name):
    """
    search for existing group_url

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_name: group name
    :type group_name: str
    :return: group object
    :rtype: `cript.nodes.Group`
    """
    # Check if Group exists
    my_groups = api.search(C.Group)
    if my_groups["count"] == 0:
        raise GroupRelatedError(
            "Error: You don't belong to any CRIPT group currently. Please contact with us."
        )

    group_search_result = api.search(C.Group, {"name": group_name})
    if group_search_result["count"] == 0 or len(group_name) == 0:
        raise GroupRelatedError(
            "Error: You must enter an existing CRIPT group. Try again."
        )
    else:
        return api.get(group_search_result["results"][0]["url"])


def upload_collection(api, group_obj, coll_name, public_flag):
    """
    search for existing collection_url, create collection if not exists

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.nodes.Group`
    :param coll_name: collection name
    :type coll_name: str
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: object of collection
    :rtype: `cript.nodes.Group`
    """
    # Check if Collection exists
    start_time = time.time()
    collection_search_result = api.search(
        C.Collection,
        {
            "group": _get_id_from_url(group_obj.url),
            "name": coll_name,
        },
    )
    print(f"search_time:{time.time() - start_time}")
    if collection_search_result["count"] > 0:
        url = collection_search_result["results"][0]["url"]
        collection_obj = api.get(url)
        print(f"get_time:{time.time() - start_time}")
    else:
        # Create Collection if it doesn't exist
        collection_obj = C.Collection(
            group=group_obj,
            name=coll_name,
            public=public_flag,
        )
        api.save(collection_obj)

    return collection_obj


def upload_experiment(api, group_obj, collection_obj, parsed_experiments, public_flag):
    """
    upload the experiment data and return url of experiment
    (WARNING: db.view() is taking all of the data in the collection out.
    It also has a default return limit of 50)
    (WARNING: currently only add supported, so there'll be duplicated data)
    (TBC: make an update on last_modified_date once update is supported)

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.nodes.Group`
    :param collection_obj: object of collection
    :type collection_obj: `cript.nodes.Collection`
    :param parsed_experiments: parsed data of experiments (experiment_sheet.parsed)
    :type parsed_experiments: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: a dict contains (experiment name) : (experiment object) pair
    :rtype: dict
    """
    experiment_objs = {}
    count = 0
    for experiment_std_name in parsed_experiments:
        # process-track
        process_track("Experiment Uploaded", count, len(parsed_experiments))

        experiment_name = parsed_experiments[experiment_std_name]["name"]

        # Search for Duplicates
        experiment_search_result = api.search(
            C.Experiment,
            {
                "group": _get_id_from_url(group_obj.url),
                "collection": _get_id_from_url(collection_obj.url),
                "name": experiment_name,
            },
        )
        if experiment_search_result["count"] > 0:
            experiment_url = experiment_search_result["results"][0]["url"]
            experiment_obj = api.get(experiment_url)
            print(f"Expriment node [{experiment_obj.name}] already exists")
        else:
            # Create Experiment
            experiment_obj = C.Experiment(
                group=group_obj,
                collection=collection_obj,
                public=public_flag,
                **parsed_experiments[experiment_std_name]["base"],
            )
            api.save(experiment_obj)

        experiment_objs[experiment_std_name] = experiment_obj

    return experiment_objs


def _create_cond_list(parsed_conds, data_objs=None):
    """
    Create a list of Cond objects.
    Used in Material,Process and Data

    :param parsed_conds: dict contains (cond) : (value dict) pair (eg.'temp': {'data': {}, 'value': 2, 'unit': 'degC'})
    :type parsed_conds: dict
    :param data_objs: dict contains (name) : (data_object) pair
    :type data_objs: dict
    :return: list of `cript.nodes.Condition` objects
    :rtype: list
    """
    conds = []
    for cond_key in parsed_conds:
        # Create Cond object
        cond = C.Condition(
            key=cond_key,
            value=parsed_conds[cond_key]["value"],
            unit=parsed_conds[cond_key].get("unit"),
        )

        # Add Data object
        parsed_data = parsed_conds[cond_key]["data"]

        if len(parsed_data) > 0:
            data_obj = data_objs[parsed_data]
            cond.data.append(data_obj)

        conds.append(cond)

    return conds


def _create_prop_list(parsed_props, data_objs=None):
    """
    Create a list of Prop objects.

    :param parsed_props: a dict contains parsed properties
    :type parsed_props: dict
    :param data_objs: dict contains (name) : (data_object) pair
    :type data_objs: dict
    :return: a list of class: `cript.Prop` objects
    :rtype: list
    """
    props = []
    for prop_key in parsed_props:
        # Create Prop object
        prop = C.Property(
            key=prop_key,
            value=parsed_props[prop_key]["value"],
            unit=parsed_props[prop_key].get("unit"),
        )

        # Add Data object
        parsed_data = parsed_props[prop_key]["data"]
        if len(parsed_data) > 0:
            data_obj = data_objs[parsed_data]
            prop.data.append(data_obj)

        # Add Cond objects
        if "cond" in parsed_props[prop_key]:
            parsed_conds = parsed_props[prop_key]["cond"]
            prop.cond = _create_cond_list(parsed_conds, data_objs)

        props.append(prop)

    return props


def _create_quantity_list(parsed_object):
    quantity_list = []
    for key in parsed_object:
        quantity_obj = C.Quantity(**parsed_object[key])
        quantity_list.append(quantity_obj)
    return quantity_list


def _replace_field(parsed_object, raw_key, replace_key):
    if raw_key in parsed_object:
        parsed_object[replace_key] = parsed_object[raw_key]
        parsed_object.pop(raw_key)


def _get_id_from_url(url: str):
    _id = url.rstrip("/").split("/")[-1]
    return str(_id)


def upload_data(api, group_obj, experiment_objs, parsed_data, public_flag):
    """
    upload data to the database and return a dict of name:data_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param experiment_objs: (name) : (object of experiment) pair
    :type experiment_objs: dict
    :param parsed_data: parsed data of data_sheet.parsed (data_sheet.parsed)
    :type parsed_data: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (name) : (object of data) pair
    :rtype: dict
    """
    data_objs = {}
    count = 0
    for data_std_name in parsed_data:
        # process-track
        process_track("Data Uploaded", count, len(parsed_data))

        parsed_datum = parsed_data[data_std_name]
        data_name = parsed_data[data_std_name]["name"]
        # Grab Experiment
        experiment_std_name = parsed_datum["experiment"].replace(" ", "").lower()
        experiment_obj = experiment_objs[experiment_std_name]

        # Search for Duplicates
        data_search_result = api.search(
            C.Data,
            {
                "group": _get_id_from_url(group_obj.url),
                "experiment": _get_id_from_url(experiment_obj.url),
                "name": data_name,
            },
        )
        if data_search_result["count"] > 0:
            url = data_search_result["results"][0]["url"]
            datum_obj = api.get(url)
            print(f"Data node [{datum_obj.name}] already exists")
        else:
            # Create Data
            datum_obj = C.Data(
                group=group_obj,
                experiment=experiment_obj,
                public=public_flag,
                **parsed_datum["base"],
            )
            # Save Data
            api.save(datum_obj)
            api.refresh(experiment_obj)

        data_objs[data_std_name] = datum_obj

    return data_objs


def upload_file(api, group_obj, data_objs, parsed_file, public_flag):
    """
    upload data to the database and return a dict of name:file_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: string
    :param data_objs: (name) : (obj of data) pair
    :type data_objs: dict
    :param parsed_file: parsed data of file_sheet.parsed
    :type parsed_file: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (name) : (obj of file) pair
    :rtype: dict
    """
    file_objs = {}
    count = 0
    for key in parsed_file:
        # process-track
        process_track("File Uploaded", count, len(parsed_file))

        file_dict = parsed_file[key]
        # Grab Data
        data_obj = data_objs[key]
        for file in file_dict:
            # Replace field name
            _replace_field(file["base"], "path", "source")
            file["base"]["source"] = file["base"]["source"]
            # Search for Duplicates
            file_search_result = api.search(
                C.File,
                {
                    "group": _get_id_from_url(group_obj.url),
                    "data": _get_id_from_url(data_obj.url),
                    "name": os.path.basename(file["base"]["source"]),
                },
            )

            if file_search_result["count"] > 0:
                url = file_search_result["results"][0]["url"]
                file_obj = api.get(url)
                print(f"File node [{file_obj.name}] already exists")
            else:
                # Create File
                file_obj = C.File(
                    group=group_obj,
                    data=data_obj,
                    public=public_flag,
                    **file["base"],
                )
                # Save Data
                api.save(file_obj)

            # Update file_urls
            if key not in file_objs:
                file_objs[key] = []
            file_objs[key].append(file_obj)

    return file_objs


def upload_material(api, group_obj, data_objs, parsed_material, public_flag):
    """
    upload material to the database and return a dict of name:material_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: obj of group
    :type group_obj: `cript.nodes.Group`
    :param data_objs: (name) : (object of data) pair
    :type data_objs: dict
    :param parsed_material: reagent_sheet.parsed or product_sheet.parsed
    :type parsed_material: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (name) : (url of material) pair
    :rtype: dict
    """
    identity_objs = {}
    material_objs = {}
    count = 0
    for material_std_name in parsed_material:
        # process-track
        process_track("Data Uploaded", count, len(parsed_material))

        material_dict = parsed_material[material_std_name]
        material_name = parsed_material[material_std_name]["name"]

        # Search for Material Node
        material_search_result = api.search(
            C.Material,
            {
                "group": _get_id_from_url(group_obj.url),
                "name": material_name,
            },
        )
        if material_search_result["count"] > 0:
            url = material_search_result["results"][0]["url"]
            material_obj = api.get(url)
            print(f"Material node [{material_obj.name}] already exists")
        else:
            component_obj = None
            # Create Component object
            if identity_objs.get(material_std_name) is not None:
                component_obj = C.Component(
                    identity=identity_objs.get(material_std_name)
                )
            # Create Material object
            material_obj = C.Material(
                group=group_obj,
                components=[component_obj] if component_obj else None,
                public=public_flag,
                **material_dict["base"],
            )

            # Add Prop objects
            parsed_props = material_dict["prop"]
            if len(parsed_props) > 0:
                material_obj.properties = _create_prop_list(parsed_props, data_objs)

            # Add Identifiers
            parsed_idens = material_dict["iden"]
            for key, value in parsed_idens.items():
                identifier = C.Identifier(key=key, value=value)
                material_obj.add_identifier(identifier)

            try:
                # Save material to DB
                api.save(material_obj)
            except Exception as e:
                print(
                    f"[WARNING]Material Save Failed."
                    f"Material:[{material_obj.name}]"
                    f"reason:{e}"
                )
                material_obj = None

        # Add saved Material object to materials dict
        material_objs[material_std_name] = material_obj

    return material_objs


def update_components(api, material_objs, parsed_components):
    for material_std_name in parsed_components:
        material_obj = material_objs.get(material_std_name)
        uid = 1
        for parsed_component in parsed_components[material_std_name]:
            component_std_name = parsed_component["component"]
            component_obj = C.Component(
                component=material_objs.get(component_std_name),
                component_uid=uid,
            )
            material_obj.add_component(component_obj)
            uid = uid + 1
        api.save(material_obj)


def upload_process(api, group_obj, experiment_objs, parsed_processes, public_flag):
    """
    upload process to the database and return a dict of name:process_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: obj of group
    :type group_obj: `cript.nodes.Group`
    :param experiment_objs: (name) : (experiment object) pair
    :type experiment_objs: dict
    :param parsed_processes:
    :type dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (name) : (url of process) pair
    :rtype: dict
    """
    process_objs = {}
    count = 0
    for experiment_std_name in parsed_processes:
        # process-track
        process_track("Process Uploaded", count, len(parsed_processes))

        # Grab Experiment
        experiment_obj = experiment_objs.get(experiment_std_name)
        process_list = parsed_processes[experiment_std_name]
        prev_process_std_name = None
        for i in range(len(process_list)):
            parsed_process = process_list[i]
            process_name = parsed_process["name"]
            process_std_name = process_name.replace(" ", "").lower()

            process_search_result = api.search(
                C.Process,
                {
                    "group": _get_id_from_url(group_obj.url),
                    "experiment": _get_id_from_url(experiment_obj.url),
                    "name": process_name,
                },
            )
            if process_search_result["count"] > 0:
                url = process_search_result["results"][0]["url"]
                process_obj = api.get(url)
                print(f"Process node [{process_obj.name}] already exists")
            else:
                # Create Process
                process_obj = C.Process(
                    group=group_obj,
                    experiment=experiment_obj,
                    public=public_flag,
                    **parsed_process["base"],
                )
                prev_process_std_name = process_std_name
                if i > 0:
                    prev_process_obj = process_objs.get(prev_process_std_name)
                    process_obj.add_dependent_process(prev_process_obj)

                # Save Process
                try:
                    api.save(process_obj)
                except Exception:
                    print(
                        f"[WARNING]Process Save Failed." f"Process:[{process_obj.name}]"
                    )
                    process_obj = None

            process_objs[process_std_name] = process_obj

    return process_objs


def update_dependent_process(api, process_objs, parsed_dependent_processes):
    for process_std_name in parsed_dependent_processes:
        process_obj = process_objs.get(process_std_name)
        dependent_process_list = parsed_dependent_processes.get(process_std_name)
        for i in range(len(dependent_process_list)):
            dependent_process_std_name = dependent_process_list[i]["dependent_process"]
            dependent_process_obj = process_objs.get(dependent_process_std_name)
            process_obj.add_dependent_process(dependent_process_obj)
        api.save(process_obj)


def upload_stepIngredient(
    api, process_objs, step_objs, material_objs, parsed_processIngredients
):
    """
    upload step to the database and return a dict of name:step_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param process_objs: (name) : (process object) pair
    :type process_objs: dict
    :param step_objs: (step_id) : (step object) pair
    :type step_objs: dict
    :param material_objs: (name) : (object of material) pair
    :type material_objs: dict
    :param parsed_processIngredients:
    :type dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    count = 0
    for process_std_name in parsed_processIngredients:
        # process-track
        process_track(
            "ProcessIngredient Uploaded", count, len(parsed_processIngredients)
        )

        # Grab Process
        process_obj = process_objs[process_std_name]

        if process_obj is None:
            continue

        for ingredient in parsed_processIngredients[process_std_name]:
            # Grab Material
            material_std_name = ingredient["material"]
            material_obj = material_objs.get(material_std_name)
            if material_obj is None:
                continue

            ingredient_obj = C.Ingredient(
                ingredient=material_obj,
                quantities=_create_quantity_list(ingredient["quantity"]),
                **ingredient["base"],
            )

            process_obj.add_ingredient(ingredient_obj)

            print(
                f"ProcessIngredient [{ingredient_obj.ingredient.name}] "
                f"has been added to Process [{process_obj.name}]"
            )

        # Save StepIngredient
        try:
            api.save(process_obj)
            print(
                f"ProcessIngredient has been saved " f"for Process [{process_obj.name}]"
            )
        except Exception:
            print(
                f"[WARNING]StepIngredient Save Failed. " f"Process:[{process_obj.name}]"
            )
            print(traceback.format_exc())


def upload_stepProduct(api, process_objs, material_objs, parsed_processProducts):
    """
    upload step to the database and return a dict of name:step_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param process_objs: (name) : (process object) pair
    :type process_objs: dict
    :param material_objs: (name) : (object of material) pair
    :type material_objs: dict
    :param parsed_processProducts:
    :type dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    count = 0
    for process_std_name in parsed_processProducts:
        # process-track
        process_track("ProcessProduct Uploaded", count, len(parsed_processProducts))

        # Grab Process
        process_obj = process_objs.get(process_std_name)
        product_list = parsed_processProducts[process_std_name]
        if process_obj is None:
            continue
        for parsed_product in product_list:
            product_std_name = parsed_product["product"]
            material_obj = material_objs.get(product_std_name)
            process_obj.add_product(material_obj)

        # Save StepProduct
        try:
            api.save(process_obj)
            # print(
            #     f"StepProduct [{mater_obj.name}] "
            #     f"has been added to Step [{step_obj.step_id}] "
            #     f"for Process [{process_obj.name}]"
            # )
        except Exception:
            # print(
            #     f"[WARNING]StepProduct Save Failed. "
            #     f"Material:[{stepProduct_obj.name}],"
            #     f"Step:[{step_obj.step_id}],"
            #     f"Process:[{process_obj.name}]"
            # )
            print(traceback.format_exc())
