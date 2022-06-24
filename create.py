from pprint import pprint

import cript
from cript.exceptions import CRIPTError
from beartype.roar import BeartypeException


error_list = []


def create_experiments(parsed_experiments, group, collection):
    experiments = {}

    for key, parsed_experiment in parsed_experiments.items():
        experiment_dict = {
            "group": group,
            "collection": collection,
        }

        for parsed_cell in parsed_experiment.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]

                if cell_type == "attribute":
                    experiment_dict[cell_key] = cell_value

        experiment = _create_object(cript.Experiment, experiment_dict, parsed_cell)
        if experiment is not None:
            experiments[key] = experiment

    return experiments


def create_citations(parsed_citations, group):
    references = {}
    citations = {}

    for key, parsed_citation in parsed_citations.items():
        reference_dict = {"group": group}

        for parsed_cell in parsed_citation.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]

                if cell_type == "attribute":
                    reference_dict[cell_key] = cell_value

        reference = _create_object(cript.Reference, reference_dict, parsed_cell)
        citation = _create_object(cript.Citation, {"reference": reference}, parsed_cell)
        if None not in (reference, citation):
            references[key] = reference
            citations[key] = citation

    return references, citations


def create_data(parsed_data, group, experiments, citations):
    data = {}
    files = {}

    for key, parsed_datum in parsed_data.items():
        datum_dict = {"group": group}

        for parsed_cell in parsed_datum.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]

                if cell_type == "attribute":
                    if cell_key == "path":
                        # Grab File object source
                        file_source = cell_value
                        continue
                    else:
                        datum_dict[cell_key] = cell_value

                elif cell_type == "relation":
                    if cell_key == "experiment":
                        datum_dict["experiment"] = _get_relation(
                            experiments, cell_value, parsed_cell
                        )

        datum = _create_object(cript.Data, datum_dict, parsed_cell)
        file = _create_object(
            cript.File,
            {
                "group": group,
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


def create_materials(parsed_materials, group, data, citations):
    materials = {}

    for key, parsed_material in parsed_materials.items():
        material_dict = {"group": group, "identifiers": [], "properties": []}

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
    for key, parsed_component in parsed_components.items():
        component_dict = {}

        for parsed_cell in parsed_component.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "relation":
                if cell_key == "mixture":
                    mixture = _get_relation(materials, cell_value, parsed_cell)

                elif cell_key == "material":
                    component_dict["material"] = _get_relation(
                        materials, cell_value, parsed_cell
                    )

        component = _create_object(cript.Component, component_dict, parsed_cell)
        if None not in (mixture, component):
            mixture.components.append(component)

    # Reorder materials so mixtures are uploaded last
    if materials:
        return {
            k: v
            for k, v in sorted(
                materials.items(), key=lambda item: len(item[1].components)
            )
        }

    return materials


def create_processes(parsed_processes, group, experiments, data, citations):
    processes = {}

    for key, parsed_process in parsed_processes.items():
        process_dict = {
            "group": group,
            "properties": [],
            "conditions": [],
        }

        for parsed_cell in parsed_process.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                process_dict[cell_key] = cell_value

            elif cell_type == "relation":
                if cell_key == "experiment":
                    process_dict["experiment"] = _get_relation(
                        experiments, cell_value, parsed_cell
                    )

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


def create_ingredients(parsed_ingredients, processes, materials):
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

            elif cell_type == "relation":
                if cell_key == "process":
                    process = _get_relation(processes, cell_value, parsed_cell)

                elif cell_key == "material":
                    ingredient_dict["material"] = _get_relation(
                        materials, cell_value, parsed_cell
                    )

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
    for key, parsed_product in parsed_products.items():
        for parsed_cell in parsed_product.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "relation":
                if cell_key == "process":
                    process = _get_relation(processes, cell_value, parsed_cell)

                if cell_key == "material":
                    material = _get_relation(materials, cell_value, parsed_cell)

        if None not in (process, material):
            process.products.append(material)


def create_prerequisites(parsed_prerequisites, processes):
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


def _create_property(parsed_property, data, citations):
    property_dict = {
        "key": parsed_property["key"],
        "value": parsed_property["value"],
        "conditions": [],
        "data": [],
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
                    property_dict["data"].append(data)

                elif cell_key == "citation":
                    citation = _get_relation(citations, cell_value, parsed_cell)
                    property_dict["citations"].append(citation)

    return _create_object(cript.Property, property_dict, parsed_cell)


def _create_condition(parsed_condition, data, citations=[]):
    condition_dict = {
        "key": parsed_condition["key"],
        "value": parsed_condition["value"],
        "data": [],
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

            elif cell_type == "relation":
                if cell_key == "data":
                    data = _get_relation(data, cell_value, parsed_cell)
                    condition_dict["data"].append(data)

                elif cell_key == "citation":
                    citation = _get_relation(citations, cell_value, parsed_cell)
                    condition_dict["citations"].append(citation)

    return _create_object(cript.Condition, condition_dict, parsed_cell)


def _create_object(obj_class, obj_dict, parsed_cell):
    try:
        return obj_class(**obj_dict)
    except (CRIPTError, BeartypeException, ValueError, TypeError) as e:
        row_index = parsed_cell["index"] + 4
        sheet_name = parsed_cell["sheet"].capitalize()
        message = f"{sheet_name} sheet, Row {row_index}: {e}"
        error_list.append(message)
        return None


def _get_relation(related_objs, cell_value, parsed_cell):
    try:
        return related_objs[cell_value]
    except KeyError:
        row_index = parsed_cell["index"] + 4
        sheet_name = parsed_cell["sheet"].capitalize()
        related_sheet = parsed_cell["key"].capitalize()
        value = parsed_cell["value"][0]
        message = f'{sheet_name} sheet, Row {row_index}: "{value}" does not exist in the {related_sheet} sheet.'
        error_list.append(message)
        return None
