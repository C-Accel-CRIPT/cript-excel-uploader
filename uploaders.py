import time
import os
import traceback

import cript as C
from config import BASE_URL
from errors import GroupRelatedError


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
        api.refresh(group_obj)

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
    for experiment_name in parsed_experiments:
        # process-track
        if count != 0 and count % 10 == 0:
            print(f"Experiment Uploaded: {count}/{len(parsed_experiments)}")
        count = count + 1

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
                **parsed_experiments[experiment_name],
            )
            api.save(experiment_obj)
            api.refresh(collection_obj)

        experiment_objs[experiment_name] = experiment_obj

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
    for data_name in parsed_data:
        # process-track
        if count != 0 and count % 10 == 0:
            print(f"Data Uploaded: {count}/{len(parsed_data)}")
        count = count + 1

        parsed_datum = parsed_data[data_name]
        # Grab Experiment
        experiment_obj = experiment_objs[parsed_datum["expt"]]

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
            # Replace field name
            _replace_field(parsed_datum["base"], "data_type", "type")
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

        data_objs[data_name] = datum_obj

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
        if count != 0 and count % 10 == 0:
            print(f"File Uploaded: {count}/{len(parsed_file)}")
        count = count + 1

        file_dict = parsed_file[key]
        # Grab Data
        data_obj = data_objs[key]
        for file in file_dict:
            # Replace field name
            _replace_field(file["base"], "path", "source")
            file["base"]["source"] = "".join(
                [char for char in file["base"]["source"] if ord(char) < 128]
            )
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
                print(f"create file node[{file}]")
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
    for material in parsed_material.values():
        # process-track
        if count != 0 and count % 10 == 0:
            print(f"Material Uploaded: {count}/{len(parsed_material)}")
        count = count + 1

        material_name = material["base"]["name"]

        # Check if Identity exists
        # Create Query
        query = {}
        cas = material["iden"].get("cas")
        if cas:
            query.update({"cas": cas})
        else:
            query.update({"name": material_name})

            smiles = material["iden"].get("smiles")
            if smiles:
                query.update({"smiles": smiles})

            bigsmiles = material["iden"].get("bigsmiles")
            if bigsmiles:
                query.update({"bigsmiles": bigsmiles})

        # Check Query is not empty
        if len(query) == 0:
            identity_obj = None
        else:
            identity_search_result = api.search(C.Identity, query)
            if identity_search_result["count"] > 0:
                # Add Identity object to identity_urls dict
                identity_url = identity_search_result["results"][0]["url"]
                identity_obj = api.get(identity_url)
                print(f"Identity node [{identity_obj.name}] already exists")
            elif len(material["iden"]) > 0:
                # Create Identity
                identity_obj = C.Identity(
                    group=group_obj,
                    public=public_flag,
                    **material["iden"],
                )
                # Save Identity
                try:
                    api.save(identity_obj)
                    print(f"Identity node [{identity_obj.name}] created")
                except Exception:
                    print(
                        f"[WARNING]Identity Save Failed."
                        f"Identity: [{identity_obj.name}]"
                    )
                    print(traceback.format_exc())
                    identity_obj = None
            else:
                identity_obj = None

        # Update identity_objs
        identity_objs[material_name] = identity_obj

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
            if identity_objs.get(material_name) is not None:
                component_obj = C.Component(identity=identity_objs.get(material_name))
            # Create Material object
            material_obj = C.Material(
                group=group_obj,
                components=[component_obj] if component_obj else None,
                public=public_flag,
                **material["base"],
            )

            # Add Prop objects
            parsed_props = material["prop"]
            if len(parsed_props) > 0:
                material_obj.properties = _create_prop_list(parsed_props, data_objs)

            try:
                # Save material to DB
                api.save(material_obj)
            except Exception:
                print(
                    f"[WARNING]Material Save Failed." f"Material:[{material_obj.name}]"
                )
                material_obj = None

        # Add saved Material object to materials dict
        material_objs[material_name] = material_obj

    return material_objs


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
    for process_name in parsed_processes:
        # process-track
        if count != 0 and count % 10 == 0:
            print(f"Process Uploaded: {count}/{len(parsed_processes)}")
        count = count + 1

        parsed_process = parsed_processes[process_name]

        # Grab Experiment
        experiment_obj = experiment_objs[parsed_process["expt"]]

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
                keywords=parsed_process.get("keywords"),
                public=public_flag,
                **parsed_process["base"],
            )
            # Save Process
            try:
                api.save(process_obj)
            except Exception:
                print(f"[WARNING]Process Save Failed." f"Process:[{process_obj.name}]")
                process_obj = None

        process_objs[process_name] = process_obj

    return process_objs


def upload_step(api, group_obj, process_objs, data_objs, parsed_steps, public_flag):
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
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (name) : (step object) pair
    :rtype: dict
    """
    step_objs = {}
    count = 0
    for process_name in parsed_steps:
        # process-track
        if count != 0 and count % 10 == 0:
            print(f"Step Uploaded: {count}/{len(parsed_steps)}")
        count = count + 1

        # Grab Process
        process_obj = process_objs[process_name]
        if process_obj is None:
            continue

        for step_id in parsed_steps[process_name]:
            parsed_step = parsed_steps[process_name][step_id]
            step_search_result = api.search(
                C.Step,
                {
                    "group": _get_id_from_url(group_obj.url),
                    "process": _get_id_from_url(process_obj.url),
                    "step_id": step_id,
                },
            )
            if step_search_result["count"] > 0:
                url = step_search_result["results"][0]["url"]
                step_obj = api.get(url)
                print(
                    f"Step node [{step_obj.step_id}] for Process [{process_obj.name}] already exists"
                )
            else:
                # Replace field name
                _replace_field(parsed_step["base"], "step_type", "type")
                _replace_field(parsed_step["base"], "step_descr", "description")
                # Create Process
                step_obj = C.Step(
                    group=group_obj,
                    process=process_obj,
                    public=public_flag,
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
                try:
                    api.save(step_obj)
                except Exception:
                    print(
                        f"[WARNING]Step Save Failed"
                        f"Step:[{step_obj.step_id}],"
                        f"Process:[{process_obj.name}]"
                    )
                    print(traceback.format_exc())
                    step_obj = None

            if process_name not in step_objs:
                step_objs[process_name] = {}
            step_objs[process_name][step_id] = step_obj

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
    count = 0
    for process_name in parsed_stepIngredients:
        # process-track
        if count != 0 and count % 10 == 0:
            print(f"StepIngredient Uploaded: {count}/{len(parsed_stepIngredients)}")
        count = count + 1

        # Grab Process
        process_obj = process_objs[process_name]
        if process_obj is None:
            continue

        for step_id in parsed_stepIngredients[process_name]:
            # Grab Step
            step_obj = step_objs[process_name][step_id]
            if step_obj is None:
                continue

            # Replace field name
            # _replace_field(parsed_step["base"], "step_type", "type")
            # _replace_field(parsed_step["base"], "step_descr", "description")
            # parsed_step["base"].pop("step_id")
            for parsed_stepIngredient in parsed_stepIngredients[process_name][step_id]:
                # Create stepIngredient
                stepIngredient_obj = None
                ingredient_name = parsed_stepIngredient.pop("ingredient")
                ingredient_name_list = ingredient_name.split(":")
                ingredient_quantities = parsed_stepIngredient.pop("quantity")
                if len(ingredient_name_list) == 1:
                    material_obj = material_objs[ingredient_name]
                    if material_obj is None:
                        continue
                    stepIngredient_obj = C.MaterialIngredient(
                        ingredient=material_obj,
                        quantity=_create_quantity_list(ingredient_quantities),
                        **parsed_stepIngredient,
                    )
                elif len(ingredient_name_list) == 2:
                    from_process_name = ingredient_name_list[0]
                    from_step_id = ingredient_name_list[1]
                    from_step_obj = step_objs[from_process_name].get(from_step_id)
                    if from_step_obj is None:
                        continue
                    stepIngredient_obj = C.IntermediateIngredient(
                        ingredient=from_step_obj,
                        quantity=_create_quantity_list(ingredient_quantities),
                        **parsed_stepIngredient,
                    )

                step_obj.add_ingredient(stepIngredient_obj)
                print(
                    f"StepIngredient [{stepIngredient_obj.ingredient.name}] "
                    f"has been added to Step [{step_obj.step_id}] "
                    f"for Process [{process_obj.name}]"
                )

            # Save StepIngredient
            try:
                api.save(step_obj)
                print(
                    f"StepIngredients has been saved "
                    f"to Step [{step_obj.step_id}] "
                    f"for Process [{process_obj.name}]"
                )
            except Exception:
                print(
                    f"[WARNING]StepIngredient Save Failed. "
                    f"Material:[{stepIngredient_obj.ingredient.name}],"
                    f"Step:[{step_obj.step_id}],"
                    f"Process:[{process_obj.name}]"
                )
                print(traceback.format_exc())


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
    count = 0
    for process_name in parsed_stepProducts:
        # process-track
        if count != 0 and count % 10 == 0:
            print(f"StepProduct Uploaded: {count}/{len(parsed_stepProducts)}")
        count = count + 1

        # Grab Process
        process_obj = process_objs.get(process_name)
        if process_obj is None:
            continue

        for step_id in parsed_stepProducts[process_name]:
            # Grab Step
            step_obj = step_objs[process_name].get(step_id)
            if step_obj is None:
                continue

            # Replace field name
            # _replace_field(parsed_step["base"], "step_type", "type")
            # _replace_field(parsed_step["base"], "step_descr", "description")
            # parsed_step["base"].pop("step_id")
            for stepProduct in parsed_stepProducts[process_name][step_id]:
                # Create stepProduct
                stepProduct_obj = material_objs.get(stepProduct["product"])
                if stepProduct_obj is None:
                    continue
                # Save StepProduct
                try:
                    step_obj.add_product(stepProduct_obj)
                    api.save(step_obj)
                    print(
                        f"StepProduct [{stepProduct_obj.name}] "
                        f"has been added to Step [{step_obj.step_id}] "
                        f"for Process [{process_obj.name}]"
                    )
                except Exception:
                    print(
                        f"[WARNING]StepProduct Save Failed. "
                        f"Material:[{stepProduct_obj.name}],"
                        f"Step:[{step_obj.step_id}],"
                        f"Process:[{process_obj.name}]"
                    )
                    print(traceback.format_exc())
