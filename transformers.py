import cript as C


def transform_experiment(group_obj, collection_obj, parsed_experiments, public_flag):
    """
    upload the experiment data and return url of experiment
    (WARNING: db.view() is taking all of the data in the collection out.
    It also has a default return limit of 50)
    (WARNING: currently only add supported, so there'll be duplicated data)
    (TBC: make an update on last_modified_date once update is supported)

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.Group`
    :param collection_obj: object of collection
    :type collection_obj: `cript.Collection`
    :param parsed_experiments: parsed data of experiments (experiment_sheet.parsed)
    :type parsed_experiments: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: a dict contains (experiment name) : (experiment object) pair
    :rtype: dict
    """
    experiment_objs = {}
    for experiment_std_name in parsed_experiments:
        # Create Experiment
        experiment_obj = C.Experiment(
            group=group_obj,
            collection=collection_obj,
            public=public_flag,
            **parsed_experiments[experiment_std_name]["base"],
        )
        experiment_objs[experiment_std_name] = experiment_obj

    return experiment_objs


def transform_data(group_obj, experiment_objs, parsed_datas, public_flag):
    """
    upload data to the database and return a dict of name:data_url pair

    :param group_obj:
    :param experiment_objs: (name) : (object of experiment) pair
    :type experiment_objs: dict
    :param parsed_datas: parsed data of data_sheet.parsed (data_sheet.parsed)
    :type parsed_datas: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (name) : (object of data) pair
    :rtype: dict
    """
    data_objs = {}
    for data_std_name in parsed_datas:
        parsed_data = parsed_datas[data_std_name]
        # Grab Experiment
        experiment_std_name = parsed_data["experiment"]
        experiment_obj = experiment_objs[experiment_std_name]

        # Create Data
        data_obj = C.Data(
            group=group_obj,
            experiment=experiment_obj,
            public=public_flag,
            **parsed_data["base"],
        )
        data_objs[data_std_name] = data_obj

    return data_objs


def transform_file(group_obj, data_objs, parsed_file, public_flag):
    """
    upload data to the database and return a dict of name:file_url pair

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.Group`
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
    for data_std_name in parsed_file:
        file_dict = parsed_file[data_std_name]
        # Grab Data
        data_obj = data_objs[data_std_name]
        for file in file_dict:
            # Create File
            file_obj = C.File(
                group=group_obj,
                data=[data_obj],
                public=public_flag,
                **file["base"],
            )
            # Update file_urls
            file_objs[file_obj.checksum] = file_obj

    return file_objs


def transform_material(group_obj, data_objs, parsed_material, public_flag, user_uid):
    """
    upload material to the database and return a dict of name:material_url pair

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
    material_objs = {}
    for material_std_name in parsed_material:

        material_dict = parsed_material[material_std_name]

        # Create Material object
        material_obj = C.Material(
            group=group_obj,
            components=[],
            public=public_flag,
            **material_dict["base"],
        )

        # Add Prop objects
        parsed_props = material_dict["prop"]
        if len(parsed_props) > 0:
            material_obj.properties = _transform_prop_list(parsed_props, data_objs)

        # Add Identifiers
        parsed_idens = material_dict["iden"]
        if len(parsed_idens) > 0:
            material_obj.identifiers = _transform_identifier_list(parsed_idens)

        # Add saved Material object to materials dict
        material_objs[material_std_name] = material_obj

    return material_objs


def transform_components(material_objs, parsed_components):
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


def transform_process(group_obj, experiment_objs, parsed_processes, public_flag):
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
    for experiment_std_name in parsed_processes:
        # Grab Experiment
        experiment_obj = experiment_objs.get(experiment_std_name)
        process_list = parsed_processes[experiment_std_name]
        prev_process_std_name = None
        for i in range(len(process_list)):
            parsed_process = process_list[i]
            process_name = parsed_process["name"]
            process_std_name = process_name.replace(" ", "").lower()

            # Create Process
            process_obj = C.Process(
                group=group_obj,
                experiment=experiment_obj,
                public=public_flag,
                **parsed_process["base"],
            )

            if i > 0:
                prev_process_obj = process_objs.get(prev_process_std_name)
                process_obj.prerequisite_processes.append(prev_process_obj)

            prev_process_std_name = process_std_name
            process_objs[process_std_name] = process_obj

    return process_objs


def transform_prerequisite_process(process_objs, parsed_prerequisite_processes):
    for process_std_name in parsed_prerequisite_processes:
        process_obj = process_objs.get(process_std_name)
        dependent_process_list = parsed_prerequisite_processes.get(process_std_name)
        for i in range(len(dependent_process_list)):
            dependent_process_std_name = dependent_process_list[i]["dependent_process"]
            dependent_process_obj = process_objs.get(dependent_process_std_name)
            process_obj.add_prerequisite_process(dependent_process_obj)


def transform_process_ingredient(
    process_objs, material_objs, parsed_processIngredients
):
    """
    upload step to the database and return a dict of name:step_url pair

    :param process_objs: (name) : (process object) pair
    :type process_objs: dict
    :param material_objs: (name) : (object of material) pair
    :type material_objs: dict
    :param parsed_processIngredients:
    :type dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    for process_std_name in parsed_processIngredients:
        # Grab Process
        process_obj = process_objs[process_std_name]

        if process_obj is None:
            continue

        for ingredient in parsed_processIngredients[process_std_name]:
            # Grab Material
            material_std_name = ingredient["ingredient"]
            material_obj = material_objs.get(material_std_name)
            if material_obj is None:
                continue

            ingredient_obj = C.Ingredient(
                ingredient=material_obj,
                quantities=_transform_quantity_list(ingredient["quan"]),
                **ingredient["base"],
            )

            process_obj.add_ingredient(ingredient_obj)


def transform_process_product(process_objs, material_objs, parsed_processProducts):
    """
    upload step to the database and return a dict of name:step_url pair

    :param process_objs: (name) : (process object) pair
    :type process_objs: dict
    :param material_objs: (name) : (object of material) pair
    :type material_objs: dict
    :param parsed_processProducts:
    :type dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    for process_std_name in parsed_processProducts:
        # Grab Process
        process_obj = process_objs.get(process_std_name)
        product_list = parsed_processProducts[process_std_name]
        if process_obj is None:
            continue
        for parsed_product in product_list:
            product_std_name = parsed_product["product"]
            material_obj = material_objs.get(product_std_name)
            process_obj.add_product(material_obj)


def _transform_cond_list(parsed_conds, data_objs=None):
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
    cond_list = []
    for cond_key in parsed_conds:
        for identifier in parsed_conds[cond_key]:
            # Create Cond object
            parent = parsed_conds[cond_key][identifier]
            cond = C.Condition(**parent["attr"])

            # Add Data object
            if "data" in parent and len(parent["data"]) > 0:
                for data_std_name in parent["data"]:
                    data_obj = data_objs[data_std_name]
                    cond.add_data(data_obj)

            cond_list.append(cond)

    return cond_list


def _transform_prop_list(parsed_props, data_objs=None):
    """
    Create a list of Prop objects.

    :param parsed_props: a dict contains parsed properties
    :type parsed_props: dict
    :param data_objs: dict contains (name) : (data_object) pair
    :type data_objs: dict
    :return: a list of class: `cript.Prop` objects
    :rtype: list
    """
    prop_list = []
    for prop_key in parsed_props:
        for identifier in parsed_props[prop_key]:
            parent = parsed_props[prop_key][identifier]

            # Create Prop object
            prop = C.Property(**parent["attr"])

            # Add Data object
            if "data" in parent and len(parent["data"]) > 0:
                for data_std_name in parent["data"]:
                    data_obj = data_objs[data_std_name]
                    prop.add_data(data_obj)

            # Add Cond objects
            if "cond" in parent and len(parent["cond"]) > 0:
                parsed_conds = parent["cond"]
                prop.cond = _transform_cond_list(parsed_conds, data_objs)

            prop_list.append(prop)

    return prop_list


def _transform_identifier_list(parsed_object):
    iden_list = []
    for key in parsed_object:
        identifier = C.Identifier(**parsed_object[key])
        iden_list.append(identifier)

    return iden_list


def _transform_quantity_list(parsed_object):
    quan_list = []
    for key in parsed_object:
        quantity_obj = C.Quantity(**parsed_object[key])
        quan_list.append(quantity_obj)
    return quan_list
