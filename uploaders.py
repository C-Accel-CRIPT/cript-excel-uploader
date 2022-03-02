import time
import sys

import cript as C
from config import BASE_URL


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
    my_groups = api.search(C.Group, {"name": group_name})
    if my_groups["count"] == 0:
        print(
            "\nError: You don't belong to any CRIPT group currently. Please contact with us."
        )
        time.sleep(5)
        sys.exit(1)

    group_search_result = api.search(C.Group, {"name": group_name})
    if group_search_result["count"] == 0:
        print("\nError: You must enter an existing CRIPT group. Try again.\n")
    else:
        return api.get(group_search_result["results"][0]["url"])


def upload_collection(api, group_obj, coll_name):
    """
    search for existing collection_url, create collection if not exists

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.nodes.Group`
    :param coll_name: collection name
    :type coll_name: str
    :return: object of collection
    :rtype: `cript.nodes.Group`
    """
    # Check if Collection exists
    start_time = time.time()
    collection_search_result = api.search(C.Collection, {"name": coll_name})
    print(f"time to search:{time.time()-start_time}")
    if collection_search_result["count"] > 0:
        obj = api.get(collection_search_result["results"][0]["url"])
        print(f"time to get:{time.time()-start_time}")
        return obj

    # Create Collection if it doesn't exist
    collection = C.Collection(group=group_obj, name=coll_name)
    api.save(collection)

    return collection


def upload_experiment(api, group_obj, collection_obj, parsed_expts):
    """
    upload the experiment data and return url of experiment
    (WARNING: db.view() is taking all of the data in the collection out.
    It also has a default return limit of 50)
    (WARNING: currently only add supported, so there'll be duplicated data)
    (TBC: make an update on last_modified_date once update is supported)

    :param api: api connection object
    :type api: class:`cript.API`
    :param collection_obj: object of collection
    :type collection_obj: `cript.nodes.Collection`
    :param parsed_expts: parsed data of experiments (experiment_sheet.parsed)
    :type parsed_expts: dict
    :return: a dict contains (experiment name) : (experiment object) pair
    :rtype: dict
    """
    expt_objs = {}
    for key in parsed_expts:
        # Create Experiment
        expt = C.Experiment(
            group=group_obj, collection=collection_obj, **parsed_expts[key]
        )
        api.save(expt)
        expt_objs[key] = expt

    return expt_objs


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
        attrs = parsed_props[prop_key]["attr"]

        # Create Prop object
        prop = C.Property(
            key=prop_key,
            value=parsed_props[prop_key]["value"],
            unit=parsed_props[prop_key].get("unit"),
            **attrs,
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
        quantity_obj = C.Quantity(key=key, **parsed_object[key])
        quantity_list.append(quantity_obj)
    return quantity_list


def _replace_field(parsed_object, raw_key, replace_key):
    if raw_key in parsed_object:
        parsed_object[replace_key] = parsed_object[raw_key]
        parsed_object.pop(raw_key)


def upload_data(api, group_obj, expt_objs, parsed_data):
    """
    upload data to the database and return a dict of name:data_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param expt_objs: (name) : (object of experiment) pair
    :type expt_objs: dict
    :param parsed_data: parsed data of data_sheet.parsed (data_sheet.parsed)
    :type parsed_data: dict
    :return: (name) : (object of data) pair
    :rtype: dict
    """
    data_objs = {}
    for key in parsed_data:
        parsed_datum = parsed_data[key]
        # Grab Experiment
        expt_obj = expt_objs[parsed_datum["expt"]]

        # Replace field name
        _replace_field(parsed_datum["base"], "data_type", "type")
        # Create Data
        datum = C.Data(
            group=group_obj,
            experiment=expt_obj,
            **parsed_datum["base"],
        )
        # Save Data
        api.save(datum)
        data_objs[key] = datum
        expt_obj.data.append(datum.url)
        api.save(expt_obj)

    return data_objs


def upload_file(api, group_obj, data_objs, parsed_file):
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
    :return: (name) : (obj of file) pair
    :rtype: dict
    """
    file_objs = {}
    for key in parsed_file:
        file_dict = parsed_file[key]
        # Grab Data
        data_obj = data_objs[key]
        for file in file_dict:
            # Replace field name
            _replace_field(file["base"], "path", "source")
            _replace_field(file["base"], "file_name", "name")
            # Create File
            file_obj = C.File(
                group=group_obj,
                data=data_obj,
                **file["base"],
            )
            # Save Data
            api.save(file_obj)
            data_obj.add_file(file_obj)
            api.save(data_obj)

            # Update file_urls
            if key not in file_objs:
                file_objs[key] = []
            file_objs[key].append(file_obj)

    return file_objs


def upload_material(api, group_obj, data_objs, parsed_material):
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
    :return: (name) : (url of material) pair
    :rtype: dict
    """
    identity_objs = {}
    material_objs = {}
    for material in parsed_material.values():
        name = material["base"]["name"]
        # Check if Identity exists
        query = {"name": name}
        cas = material["iden"].get("cas")
        if cas:
            query.update({"cas": cas})
        smiles = material["iden"].get("smiles")
        if smiles:
            query.update({"smiles": smiles})

        check = api.search(C.Identity, query)

        if check["count"] > 0:
            # Add Identity object to identity_urls dict
            identity_url = str(check["results"][0]["url"])
            identity_objs[name] = api.get(identity_url)
        else:
            # Create Identity
            identity_obj = C.Identity(group=group_obj, **material["iden"])
            # Save Identity
            api.save(identity_obj)
            # Update identity_urls
            identity_objs[name] = identity_obj

        # Create Component object
        component = C.Component(identity=identity_objs[name])
        # Create Material object
        material_obj = C.Material(
            group_obj,
            components=[component],
            **material["base"],
        )

        # Add Prop objects
        parsed_props = material["prop"]
        if len(parsed_props) > 0:
            material_obj.properties = _create_prop_list(parsed_props, data_objs)

        # Save material to DB
        try:
            api.save(material_obj)
        except AttributeError as e:
            print(
                f"AttributeError when saving '{material_obj.name}': {e}\nContinuing anyways..."
            )

        # Add saved Material object to materials dict
        material_objs[material_obj.name] = material_obj

    return material_objs


def upload_process(api, group_obj, expt_objs, parsed_processes):
    """
    upload process to the database and return a dict of name:process_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: obj of group
    :type group_obj: `cript.nodes.Group`
    :param expt_objs: (name) : (experiment object) pair
    :type expt_objs: dict
    :param parsed_processes:
    :type dict
    :return: (name) : (url of process) pair
    :rtype: dict
    """
    process_objs = {}
    for key in parsed_processes:
        parsed_process = parsed_processes[key]

        # Grab Experiment
        expt_obj = expt_objs[parsed_process["expt"]]

        # Replace field name
        # _replace_field(parsed_datum["base"], "data_type", "type")
        # Create Process
        process_obj = C.Process(
            group=group_obj,
            experiment=expt_obj,
            keywords=parsed_process.get("keywords"),
            **parsed_process["base"],
        )
        # Save Process
        api.save(process_obj)
        process_objs[key] = process_obj

    return process_objs


def upload_step(api, group_obj, process_objs, data_objs, parsed_steps):
    """
    upload step to the database and return a dict of name:step_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: obj of group
    :type group_obj: `cript.nodes.Group`
    :param process_objs: (name) : (process object) pair
    :type process_objs: dict
    :param data_objs: (name) : (object of data) pair
    :type data_objs: dict
    :param parsed_steps:
    :type dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    step_objs = {}
    for key in parsed_steps:
        # Grab Process
        process_obj = process_objs[key]

        for step_id in parsed_steps[key]:
            parsed_step = parsed_steps[key][step_id]

            # Replace field name
            _replace_field(parsed_step["base"], "step_type", "type")
            _replace_field(parsed_step["base"], "step_descr", "description")
            parsed_step["base"].pop("step_id")
            # Create Process
            step_obj = C.Step(
                group=group_obj,
                process=process_obj,
                **parsed_step["base"],
            )

            # Add Prop objects
            parsed_props = parsed_step["prop"]
            if len(parsed_props) > 0:
                step_obj.properties = _create_prop_list(parsed_props, data_objs)

            # Add Cond objects
            parsed_conds = parsed_step["cond"]
            if len(parsed_conds) > 0:
                step_obj.conditions = _create_cond_list(parsed_conds, data_objs)

            # Save Process
            api.save(step_obj)
            if key not in step_objs:
                step_objs[key] = {}
            step_objs[key][step_id] = step_obj

    return step_objs


def upload_stepIngredient(
    api, process_objs, step_objs, material_objs, parsed_stepIngredients
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
    :param parsed_stepIngredients:
    :type dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    for process_name in parsed_stepIngredients:
        # Grab Process
        process_obj = process_objs[process_name]
        for step_id in parsed_stepIngredients[process_name]:
            # Grab Step
            step_obj = step_objs[process_name][step_id]

            # Replace field name
            # _replace_field(parsed_step["base"], "step_type", "type")
            # _replace_field(parsed_step["base"], "step_descr", "description")
            # parsed_step["base"].pop("step_id")
            for parsed_stepIngredient in parsed_stepIngredients[process_name][step_id]:
                # Create stepIngredient
                stepIngredient_obj = None
                print(parsed_stepIngredient)
                ingredient_name = parsed_stepIngredient.pop("ingredient")
                ingredient_name_list = ingredient_name.split(":")
                ingredient_quantities = parsed_stepIngredient.pop("quantity")
                if len(ingredient_name_list) == 1:
                    material_obj = material_objs[ingredient_name]
                    stepIngredient_obj = C.MaterialIngredient(
                        ingredient=material_obj,
                        quantity=_create_quantity_list(ingredient_quantities),
                        **parsed_stepIngredient,
                    )

                elif len(ingredient_name_list) == 2:
                    from_process_name = ingredient_name_list[0]
                    from_step_id = ingredient_name_list[1]
                    from_step_obj = step_objs[from_process_name][from_step_id]
                    stepIngredient_obj = C.IntermediateIngredient(
                        ingredient=from_step_obj,
                        quantity=_create_quantity_list(ingredient_quantities),
                        **parsed_stepIngredient,
                    )

                # Save StepIngredient
                step_obj.add_ingredient(stepIngredient_obj)
            api.save(step_obj)


def upload_stepProduct(
    api, process_objs, step_objs, material_objs, parsed_stepProducts
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
    :param parsed_stepProducts:
    :type dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    for process_name in parsed_stepProducts:
        # Grab Process
        process_obj = process_objs[process_name]
        for step_id in parsed_stepProducts[process_name]:
            # Grab Step
            step_obj = step_objs[process_name][step_id]

            # Replace field name
            # _replace_field(parsed_step["base"], "step_type", "type")
            # _replace_field(parsed_step["base"], "step_descr", "description")
            # parsed_step["base"].pop("step_id")
            for parsed_stepProducts in parsed_stepProducts[process_name][step_id]:
                # Create stepIngredient
                stepProduct_obj = material_objs[parsed_stepProducts["product"]]

                # Save StepIngredient
                step_obj.add_product(stepProduct_obj)
            api.save(step_obj)
