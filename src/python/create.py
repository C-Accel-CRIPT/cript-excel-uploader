import cript
from beartype.roar import BeartypeException
from cript.exceptions import CRIPTError

error_list = []


def create_experiments(parsed_experiments, collection, public):
    """Compiles a dictionary of cript Experiment objects. If a parsed experiment is able to be turned
    into an Experiment object it is added to an experiments dictionary and that dictionary is returned.
    parsed_...-dict of dicts
    group-object
    collection-object
    public-bool, Privacy flag for the object.
    returns- dict of objects"""
    experiments = {}

    for key, parsed_experiment in parsed_experiments.items():
        experiment_dict = {"collection": collection, "public": public}

        for parsed_cell in parsed_experiment.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]
                # Only attribute types should be in Experiment
                if cell_type == "attribute":
                    experiment_dict[cell_key] = cell_value

        experiment = _create_object(cript.Experiment, experiment_dict, parsed_cell)
        # Only adds Experiment objects
        if experiment is not None:
            experiments[key] = experiment

    return experiments


def create_citations(parsed_citations, group, public):
    """Compiles dictionaries with Data and File cript objects.
    parsed_...-dict of dicts
    group-obj
    public-bool, Privacy flag for the object.
    returns-tuple of dicts of objs
    """

    references = {}
    citations = {}

    for key, parsed_citation in parsed_citations.items():
        reference_dict = {"group": group, "public": public}

        for parsed_cell in parsed_citation.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]
                # All recognized fields in citation are attribute types
                if cell_type == "attribute":
                    reference_dict[cell_key] = cell_value
        # Attempts to create a Reference object that would be added to a Citation object
        reference = _create_object(cript.Reference, reference_dict, parsed_cell)
        citation = _create_object(cript.Citation, {"reference": reference}, parsed_cell)
        if None not in (reference, citation):
            references[key] = reference
            citations[key] = citation

    return references, citations


def create_data(parsed_data, project, experiments, citations, public):
    """Compiles dictionaries with Data and File cript objects.
    parsed_...-dict of dicts
    project-obj
    experiments-dict of objs
    public-bool, Privacy flag for the object.
    returns-tuple of dicts of objs
    """
    data = {}
    files = {}

    for key, parsed_datum in parsed_data.items():
        datum_dict = {"citations": [], "public": public}

        for parsed_cell in parsed_datum.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]

                if cell_type == "attribute":
                    if cell_key == "source":
                        # Grab File object source
                        file_source = cell_value
                        continue
                    else:
                        datum_dict[cell_key] = cell_value

                elif cell_type == "relation":
                    # Relates the data to an experiment object it is connected to
                    if cell_key == "experiment":
                        datum_dict["experiment"] = _get_relation(
                            experiments, cell_value, parsed_cell
                        )

                    elif cell_key == "citation":
                        citation = _get_relation(citations, cell_value, parsed_cell)
                        datum_dict["citations"].append(citation)
                    # Marks cell as None for now, and will be updated later once Process Nodes are created
                    elif cell_key == "sample_preparation":
                        datum_dict["sample_preparation"] = None

        datum = _create_object(cript.Data, datum_dict, parsed_cell)
        file = _create_object(
            cript.File,
            {
                "project": project,
                "data": [datum],
                "source": file_source,
                "type": "data",
            },
            parsed_cell,
        )
        if None not in (datum, file):
            data[key] = datum
            files[key] = file

    return data, files


def create_materials(parsed_materials, project, data, citations, public):
    """Creates Material objects and adds them to a dictionary of Material objects if possible.
    Returns dictionary of Material objects
    parsed_..-dict of dicts
    project-obj
    data-obj
    citations-list
    public-bool, Privacy flag for the object.
    return-dict of obj"""
    materials = {}

    for key, parsed_material in parsed_materials.items():
        material_dict = {
            "project": project,
            "identifiers": [],
            "properties": [],
            "public": public,
        }

        for parsed_cell in parsed_material.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                material_dict[cell_key] = cell_value

            elif cell_type == "identifier":
                identifier = _create_object(
                    cript.Identifier,
                    {"key": cell_key, "value": cell_value},
                    parsed_cell,
                )
                material_dict["identifiers"].append(identifier)

            elif cell_type == "property":
                property = _create_property(parsed_cell, data, citations)
                material_dict["properties"].append(property)

        material = _create_object(cript.Material, material_dict, parsed_cell)
        if material is not None:
            materials[key] = material

    return materials


def create_mixtures(parsed_components, materials):
    """Creates component objects for mixtures to be added to a material object
    parsed_..-dict of dicts
    materials-dict of objs"""
    for key, parsed_component in parsed_components.items():
        for parsed_cell in parsed_component.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "relation":
                if cell_key == "mixture":
                    mixture = _get_relation(materials, cell_value, parsed_cell)

                elif cell_key == "material":
                    component = _get_relation(materials, cell_value, parsed_cell)

        if None not in (mixture, component):
            mixture.components.append(component)

    # Reorder materials so mixtures are uploaded last
    # Mixtures must be uploaded last in order to ensure Components can be accessed
    if materials:
        return {
            k: v
            for k, v in sorted(
                materials.items(), key=lambda item: len(item[1].components)
            )
        }

    return materials


def create_processes(parsed_processes, experiments, data, citations, public):
    """Creates a dictionary of Process objects to be returned.
    parsed_...-dict of objects
    experiments-dict of objects
    data-obj
    citations-list
    public-bool, Privacy flag for the object.
    returns dict of objects"""
    processes = {}

    for key, parsed_process in parsed_processes.items():
        process_dict = {
            "properties": [],
            "conditions": [],
            "public": public,
        }

        for parsed_cell in parsed_process.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                process_dict[cell_key] = cell_value

            # Gets existing object if available
            elif cell_type == "relation":
                if cell_key == "experiment":
                    process_dict["experiment"] = _get_relation(
                        experiments, cell_value, parsed_cell
                    )

            # Creates objects that will go into process node
            elif cell_type == "property":
                property = _create_property(parsed_cell, data, citations)
                process_dict["properties"].append(property)

            elif cell_type == "condition":
                condition = _create_condition(parsed_cell, data, citations)
                process_dict["conditions"].append(condition)

        process = _create_object(cript.Process, process_dict, parsed_cell)
        if process is not None:
            processes[key] = process

    return processes


def create_prerequisites(parsed_prerequisites, processes):
    """Attaches prerequisite process information to a Process node.
    parsed_...-dict of dicts
    processes-dict of objs"""
    for key, parsed_prerequisite in parsed_prerequisites.items():
        for parsed_cell in parsed_prerequisite.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "relation":
                if cell_key == "process":
                    process = _get_relation(processes, cell_value, parsed_cell)

                elif cell_key == "prerequisite":
                    prerequisite = _get_relation(processes, cell_value, parsed_cell)

        if None not in (process, prerequisite):
            process.prerequisite_processes.append(prerequisite)


def create_ingredients(parsed_ingredients, processes, materials):
    """Creates a dictionary of Ingredient objects to be returned.
    parsed_...-dict of dicts
    processes-dict of objs
    materials-dict of objs
    """
    for key, parsed_ingredient in parsed_ingredients.items():
        ingredient_dict = {
            "quantities": [],
        }

        for parsed_cell in parsed_ingredient.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                ingredient_dict[cell_key] = cell_value
            # Gets related objects to be included in node
            elif cell_type == "relation":
                if cell_key == "process":
                    process = _get_relation(processes, cell_value, parsed_cell)

                elif cell_key == "material":
                    ingredient_dict["material"] = _get_relation(
                        materials, cell_value, parsed_cell
                    )
            # Creates Quantity node
            elif cell_type == "quantity":
                quantity = _create_object(
                    cript.Quantity,
                    {
                        "key": cell_key,
                        "value": cell_value,
                        "unit": parsed_cell["unit"],
                    },
                    parsed_cell,
                )
                if quantity is not None:
                    ingredient_dict["quantities"].append(quantity)

        ingredient = _create_object(cript.Ingredient, ingredient_dict, parsed_cell)
        if None not in (process, ingredient):
            process.ingredients.append(ingredient)


def create_products(parsed_products, processes, materials):
    """Attaches material product to its related process
    parsed_...-dict of dicts
    processes-dict of objs
    materials-dict of objs"""
    for key, parsed_product in parsed_products.items():
        for parsed_cell in parsed_product.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]
            # Gets related objects
            if cell_type == "relation":
                if cell_key == "process":
                    process = _get_relation(processes, cell_value, parsed_cell)

                if cell_key == "material":
                    material = _get_relation(materials, cell_value, parsed_cell)

        if None not in (process, material):
            process.products.append(material)


def create_equipment(parsed_equipment, processes, data, citations):
    """Attaches equipment to its related process
    parsed_equipment-dict of dicts
    processes-dict of objs"""
    for key, parsed_piece in parsed_equipment.items():
        piece_dict = {"conditions": [], "citations": []}

        for parsed_cell in parsed_piece.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                piece_dict[cell_key] = cell_value

            # Gets existing object if available
            elif cell_type == "relation":
                if cell_key == "process":
                    process = _get_relation(processes, cell_value, parsed_cell)

            elif cell_type == "condition":
                condition = _create_condition(parsed_cell, data, citations)
                piece_dict["conditions"].append(condition)

            elif cell_key == "citation":
                citation = _get_relation(citations, cell_value, parsed_cell)
                piece_dict["citations"].append(citation)

        piece = _create_object(cript.Equipment, piece_dict, parsed_cell)
        if None not in (process, piece):
            process.equipment.append(piece)


def _create_property(parsed_property, data, citations):
    """Tries to create a Property object that contains plain attributes as well as other
    objects within. Returns Property object or None.
    parsed_...-dict
    data-obj
    citations-list
    returns-object or None
    """
    property_dict = {
        "key": parsed_property["key"],
        "value": parsed_property["value"],
        "conditions": [],
        "citations": [],
    }
    if parsed_property["unit"]:
        property_dict.update({"unit": parsed_property["unit"]})

    for parsed_cell in parsed_property.values():
        if isinstance(parsed_cell, dict):
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                property_dict[cell_key] = cell_value

            elif cell_type == "condition":
                condition = _create_condition(parsed_cell, data)
                property_dict["conditions"].append(condition)

            elif cell_type == "relation":
                if cell_key == "data":
                    data = _get_relation(data, cell_value, parsed_cell)
                    property_dict["data"] = data

                elif cell_key == "citation":
                    citation = _get_relation(citations, cell_value, parsed_cell)
                    property_dict["citations"].append(citation)

    return _create_object(cript.Property, property_dict, parsed_cell)


def _create_condition(parsed_condition, data, citations=[]):
    """Creates a condition node and returns if possible.
    parsed_...-dict
    data-obj
    citations-list
    returns-object or None"""
    condition_dict = {
        "key": parsed_condition["key"],
        "value": parsed_condition["value"],
    }
    if parsed_condition["unit"]:
        condition_dict.update({"unit": parsed_condition["unit"]})

    for parsed_cell in parsed_condition.values():
        if isinstance(parsed_cell, dict):
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                condition_dict[cell_key] = cell_value
            # Gets and stores objects for valid related objects
            elif cell_type == "relation":
                if cell_key == "data":
                    data = _get_relation(data, cell_value, parsed_cell)
                    condition_dict["data"] = data

                elif cell_key == "citation":
                    citation = _get_relation(citations, cell_value, parsed_cell)
                    condition_dict["citations"].append(citation)

    return _create_object(cript.Condition, condition_dict, parsed_cell)


def _create_object(obj_class, obj_dict, parsed_cell):
    """Tries to create and return a cript object.
    obj_class-class
    obj_dict-dict
    parsed_cell-dict
    return-object or None"""
    try:
        # Returns a successfully created cript object
        return obj_class(**obj_dict)
    except (
        CRIPTError,
        BeartypeException,
        ValueError,
        TypeError,
        FileNotFoundError,
    ) as e:
        # Updates list of error messages to show to user and returns None if an object
        # couldn't be created
        row_index = parsed_cell["index"] + 4
        sheet_name = parsed_cell["sheet"].capitalize()
        message = f"{sheet_name} sheet, Row {row_index}: {e}"
        error_list.append(message)
        return None


def _get_relation(related_objs, cell_value, parsed_cell):
    """Tries to get and return an object created from another sheet by
    indexing into the dictionary where the object is stored.
    related_objs-dict of dicts,
    cell_value-str
    parsed_cell-dict
    return-object or None
    """
    try:
        # returns related object if possible
        return related_objs[cell_value]
    except KeyError:
        # Adds error to list of errors and returns None
        # Add 4 due to differences in DataFrame and excel format
        row_index = parsed_cell["index"] + 4
        sheet_name = parsed_cell["sheet"].capitalize()
        related_sheet = parsed_cell["key"].capitalize()
        value = parsed_cell["value"][0]
        message = f'{sheet_name} sheet, Row {row_index}: "{value}" does not exist in the {related_sheet} sheet.'
        error_list.append(message)
        return None
