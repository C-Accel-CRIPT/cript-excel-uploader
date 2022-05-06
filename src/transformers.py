import cript as C
from src.errors import CreatOrUpdateNodeError


def transform_experiment(group_obj, collection_obj, parsed_experiments, public_flag):
    """
    create experiment objects locally and return a dict of name: experiment object pair

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
        try:
            experiment_obj = C.Experiment(
                group=group_obj,
                collection=collection_obj,
                public=public_flag,
                **parsed_experiments[experiment_std_name]["base"],
            )
        except Exception as e:
            node_type = "Experiment"
            sheet = "Experiment"
            idx = parsed_experiments[experiment_std_name]["index"]
            print(
                CreatOrUpdateNodeError(
                    msg=e.__str__(),
                    idx=idx,
                    node_type=node_type,
                    sheet=sheet,
                ).__str__()
            )
            experiment_obj = None
        experiment_objs[experiment_std_name] = experiment_obj

    return experiment_objs


def transform_data(group_obj, experiment_objs, parsed_datas, public_flag):
    """
    create data object locally and return a dict of name:data object pair

    :param group_obj: object of group
    :type group_obj: `cript.Group`
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

        try:
            # Create Data
            data_obj = C.Data(
                group=group_obj,
                experiment=experiment_obj,
                public=public_flag,
                **parsed_data["base"],
            )
        except Exception as e:
            node_type = "Data"
            sheet = "Data"
            idx = parsed_data["index"]
            print(
                CreatOrUpdateNodeError(
                    msg=e.__str__(),
                    idx=idx,
                    node_type=node_type,
                    sheet=sheet,
                ).__str__()
            )
            data_obj = None

        data_objs[data_std_name] = data_obj

    return data_objs


def transform_file(group_obj, data_objs, parsed_file, public_flag):
    """
    create file objects and return a dict of name:file object pair

    :param group_obj: object of group
    :type group_obj: `cript.Group`
    :param data_objs: (name) : (object of data) pair
    :type data_objs: dict
    :param parsed_file: parsed data of file_sheet.parsed
    :type parsed_file: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (checksum) : (object of file) pair
    :rtype: dict
    """
    file_objs = {}
    for data_std_name in parsed_file:
        file_dict = parsed_file[data_std_name]
        # Grab Data
        data_obj = data_objs[data_std_name]
        for file in file_dict:
            # Create File
            try:
                file_obj = C.File(
                    group=group_obj,
                    data=[data_obj],
                    public=public_flag,
                    **file["base"],
                )
            except Exception as e:
                node_type = "File"
                sheet = "File"
                idx = file["index"]
                print(
                    CreatOrUpdateNodeError(
                        msg=e.__str__(),
                        idx=idx,
                        node_type=node_type,
                        sheet=sheet,
                    ).__str__()
                )
                file_obj = None

            # Update file_urls
            file_objs[file_obj.checksum] = file_obj

    return file_objs


def transform_material(group_obj, data_objs, parsed_materials, public_flag):
    """
    create material objects locally and return a dict of name:material_object pair

    :param group_obj: object of group
    :type group_obj: `cript.Group`
    :param data_objs: (name) : (object of data) pair
    :type data_objs: dict
    :param parsed_materials: material_sheet.parsed
    :type parsed_materials: dict
    :param public_flag: a boolean flag allow users to set whether the data to go public/private
    :type public_flag: bool
    :return: (name) : (object of material) pair
    :rtype: dict
    """
    material_objs = {}
    for material_std_name in parsed_materials:

        parsed_material = parsed_materials[material_std_name]

        try:
            # Create Material object
            material_obj = C.Material(
                group=group_obj,
                components=[],
                public=public_flag,
                **parsed_material["base"],
            )

            # Add Prop objects
            parsed_props = parsed_material.get("prop")
            if parsed_props is not None and len(parsed_props) > 0:
                material_obj.properties = _transform_prop_list(parsed_props, data_objs)

            # Add Identifiers
            parsed_idens = parsed_material.get("iden")
            if parsed_idens is not None and len(parsed_idens) > 0:
                material_obj.identifiers = _transform_identifier_list(parsed_idens)
        except Exception as e:
            node_type = "Material"
            sheet = "Material"
            idx = parsed_material["index"]
            print(
                CreatOrUpdateNodeError(
                    msg=e.__str__(),
                    idx=idx,
                    node_type=node_type,
                    sheet=sheet,
                ).__str__()
            )
            material_obj = None
        # Add saved Material object to materials dict
        material_objs[material_std_name] = material_obj

    return material_objs


def transform_components(material_objs, parsed_components):
    """
    update components for material objects
    :param material_objs: (name) : (object of material) pair
    :type material_objs: dict
    :param parsed_components: component_sheet.parsed
    :type parsed_components: dict
    """
    for material_std_name in parsed_components:
        material_obj = material_objs.get(material_std_name)
        uid = 1
        for parsed_component in parsed_components[material_std_name]:
            component_std_name = parsed_component["component"]
            try:
                component_obj = C.Component(
                    component=material_objs.get(component_std_name),
                    component_uid=uid,
                )
                material_obj.add_component(component_obj)
                uid = uid + 1
            except Exception as e:
                node_type = "Component"
                sheet = "mixture component"
                idx = parsed_component["index"]
                print(
                    CreatOrUpdateNodeError(
                        msg=e.__str__(),
                        idx=idx,
                        node_type=node_type,
                        sheet=sheet,
                    ).__str__()
                )


def transform_process(
    group_obj, experiment_objs, data_objs, parsed_processes, public_flag
):
    """
    create process objects locally and return a dict of name:process object pair

    :param group_obj: object of group
    :type group_obj: `cript.Group`
    :param experiment_objs: (name): (experiment object) pair
    :type experiment_objs: dict
    :param parsed_processes: process_sheet.parsed
    :type parsed_processes: dict
    :param data_objs: (name): (data object) pair
    :type data_objs: dict
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
            try:
                # Create Process
                process_obj = C.Process(
                    group=group_obj,
                    experiment=experiment_obj,
                    public=public_flag,
                    **parsed_process["base"],
                )
                # Add Prop objects
                parsed_props = parsed_process.get("prop")
                if parsed_props is not None and len(parsed_props) > 0:
                    process_obj.properties = _transform_prop_list(
                        parsed_props, data_objs
                    )

                # Add Cond objects
                parsed_conds = parsed_process.get("cond")
                if parsed_conds is not None and len(parsed_conds) > 0:
                    process_obj.conditions = _transform_cond_list(
                        parsed_conds, data_objs
                    )

                # Set prerequisite process
                if i > 0:
                    prev_process_obj = process_objs.get(prev_process_std_name)
                    process_obj.prerequisite_processes.append(prev_process_obj)
            except Exception as e:
                node_type = "Process"
                sheet = "process"
                idx = parsed_process["index"]
                print(
                    CreatOrUpdateNodeError(
                        msg=e.__str__(),
                        idx=idx,
                        node_type=node_type,
                        sheet=sheet,
                    ).__str__()
                )
                process_obj = None

            prev_process_std_name = process_std_name
            process_objs[process_std_name] = process_obj

    return process_objs


def transform_prerequisite_process(process_objs, parsed_prerequisite_processes):
    """
    Update prerequisite process for process objects
    :param process_objs: (name): (process object) pair
    :type process_objs: dict
    :param parsed_prerequisite_processes: prerequisite_process_sheet.parsed
    """

    for process_std_name in parsed_prerequisite_processes:
        process_obj = process_objs.get(process_std_name)
        prerequisite_process_list = parsed_prerequisite_processes.get(process_std_name)
        for i in range(len(prerequisite_process_list)):
            prerequisite_process_std_name = prerequisite_process_list[i][
                "prerequisite_process"
            ]
            prerequisite_process_obj = process_objs.get(prerequisite_process_std_name)
            try:
                process_obj.add_prerequisite_process(prerequisite_process_obj)
            except Exception as e:
                node_type = "Process"
                sheet = "prerequisite process"
                idx = prerequisite_process_list[i]["index"]
                print(
                    CreatOrUpdateNodeError(
                        msg=e.__str__(),
                        idx=idx,
                        node_type=node_type,
                        sheet=sheet,
                    ).__str__()
                )


def transform_process_ingredient(
    process_objs, material_objs, parsed_process_ingredients
):
    """
    upload ingre to the database and return a dict of name:step_url pair

    :param process_objs: (name) : (process object) pair
    :type process_objs: dict
    :param material_objs: (name) : (object of material) pair
    :type material_objs: dict
    :param parsed_process_ingredients:
    :type parsed_process_ingredients: dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    for process_std_name in parsed_process_ingredients:
        # Grab Process
        process_obj = process_objs[process_std_name]

        if process_obj is None:
            continue

        for parsed_ingredient in parsed_process_ingredients[process_std_name]:
            # Grab Material
            material_std_name = parsed_ingredient["ingredient"]
            material_obj = material_objs.get(material_std_name)
            if material_obj is None:
                continue
            try:
                ingredient_obj = C.Ingredient(
                    ingredient=material_obj,
                    quantities=_transform_quantity_list(parsed_ingredient["quan"]),
                    **parsed_ingredient["base"],
                )
                process_obj.add_ingredient(ingredient_obj)
            except Exception as e:
                node_type = "Ingredient"
                sheet = "process ingredient"
                idx = parsed_ingredient["index"]
                print(
                    CreatOrUpdateNodeError(
                        msg=e.__str__(),
                        idx=idx,
                        node_type=node_type,
                        sheet=sheet,
                    ).__str__()
                )


def transform_process_product(process_objs, material_objs, parsed_process_products):
    """
    update product object to

    :param process_objs: (name) : (process object) pair
    :type process_objs: dict
    :param material_objs: (name) : (object of material) pair
    :type material_objs: dict
    :param parsed_process_products: process_product_sheet.parsed
    :type parsed_process_products: dict
    :return: (name) : (step object) pair
    :rtype: dict
    """
    for process_std_name in parsed_process_products:
        # Grab Process
        process_obj = process_objs.get(process_std_name)
        product_list = parsed_process_products[process_std_name]
        if process_obj is None:
            continue
        for parsed_product in product_list:
            product_std_name = parsed_product["product"]
            material_obj = material_objs.get(product_std_name)
            try:
                process_obj.add_product(material_obj)
            except Exception as e:
                node_type = "Product"
                sheet = "process product"
                idx = parsed_product["index"]
                print(
                    CreatOrUpdateNodeError(
                        msg=e.__str__(),
                        idx=idx,
                        node_type=node_type,
                        sheet=sheet,
                    ).__str__()
                )


def _transform_cond_list(parsed_conds, data_objs):
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


def _transform_prop_list(parsed_props, data_objs):
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
