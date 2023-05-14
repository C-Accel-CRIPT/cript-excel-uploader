import cript
from beartype.roar import BeartypeException
from cript.exceptions import CRIPTError

error_list = []
row_input_can_start_from = 5


def create_experiments_and_inventories(parsed_experiments, collection):
    """Compiles dictionaries of CRIPT Experiment objects and CRIPT Inventory objects. If a parsed experiment/inventory is able to be turned
    into an Experiment/Inventory object it is added to an experiments dictionary and that dictionary is returned.
    parsed_...-dict of dicts
    group-object
    collection-object
    returns- dict of objects"""
    experiments = {}
    inventories = {}

    for key, parsed_experiment in parsed_experiments.items():
        experiment_dict = {"collection": collection}
        inventory_dict = {"collection": collection}
        inventory = False
        for parsed_cell in parsed_experiment.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]
                # Only attribute and that specific identifier should be in experiment
                if cell_type == "attribute":
                    experiment_dict[cell_key] = cell_value
                    inventory_dict[cell_key] = cell_value
                elif cell_type == "identifier":
                    if cell_key == "Experiment or Inventory":
                        if cell_value.lower() == "i":
                            inventory = True
        if inventory:
            invObj = _create_object(cript.Inventory, inventory_dict, parsed_cell)
            if invObj is not None:
                inventories[key] = invObj
        else:
            experiment = _create_object(cript.Experiment, experiment_dict, parsed_cell)
            # Only adds Experiment objects
            if experiment is not None:
                experiments[key] = experiment

    return experiments, inventories


def create_citations(parsed_citations, group):
    """Compiles dictionaries with Data and File cript objects.
    parsed_...-dict of dicts
    group-cript Group node
    returns-tuple of dicts of reference nodes and citation nodes
    """

    references = {}
    citations = {}

    for key, parsed_citation in parsed_citations.items():
        reference_dict = {"group": group}

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


def create_data(parsed_data, project, experiments, citations):
    """Compiles dictionaries with Data and File cript objects.
    parsed_...-dict of dicts
    project-obj
    experiments-dict of objs
    returns-tuple of dicts of objs
    """
    data = {}
    files = {}

    for key, parsed_datum in parsed_data.items():
        datum_dict = {"files": [], "citations": []}
        files_list = []
        for parsed_cell in parsed_datum.values():
            if isinstance(parsed_cell, dict):
                cell_type = parsed_cell["type"]
                cell_key = parsed_cell["key"]
                cell_value = parsed_cell["value"]

                if cell_type == "attribute":
                    if cell_key == "source":
                        # Grab File object source
                        file_source = cell_value
                        files_list.append(
                            _create_object(
                                cript.File,
                                {
                                    "project": project,
                                    "source": file_source,
                                    "type": "data",
                                },
                                parsed_cell,
                            )
                        )

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

        if None not in files_list:
            files[key] = files_list

        datum = _create_object(cript.Data, datum_dict, parsed_cell)

        if datum:
            data[key] = datum

    return data, files


def create_materials(parsed_materials, project, data, citations):
    """Creates Material objects and adds them to a dictionary of Material objects if possible.
    Returns dictionary of Material objects
    parsed_..-dict of dicts
    project-obj
    data-obj
    citations-list
    return-dict of obj"""
    materials = {}
    inventory_dict = {}

    for key, parsed_material in parsed_materials.items():
        use_existing = False
        material_dict = {
            "project": project,
            "identifiers": [],
            "properties": [],
        }
        belongs_in_inv = False
        inv_name = None

        for parsed_cell in parsed_material.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":

                if cell_key == "computational_forcefield":
                    material_dict[cell_key] = create_computational_forcefield(
                        parsed_cell
                    )
                else:
                    material_dict[cell_key] = cell_value

            elif cell_type == "identifier":
                identifier = _create_object(
                    cript.Identifier,
                    {"key": cell_key, "value": cell_value},
                    parsed_cell,
                )
                material_dict["identifiers"].append(identifier)

            elif cell_type == "property":
                if parsed_cell["key"] == "use_existing":
                    use_existing = is_cell_true(parsed_cell["value"])
                    continue
                property = _create_property(parsed_cell, data, citations)
                material_dict["properties"].append(property)
            elif cell_type == "relation":
                belongs_in_inv = True
                inv_name = cell_value

        # Add characteristics to an already created material node
        if use_existing:

            try:
                # try to get the material using its name
                mat_name = parsed_material["name"]["value"]
                new_project = cript.Project.get(
                    name=parsed_material["use_existing"]["value"]
                )
                material = cript.Material.get(name=mat_name, project=new_project.uid)

            # If there is a get error add it to the errors sheet
            except ValueError as e:
                row_index = parsed_cell["index"] + row_input_can_start_from
                sheet_name = parsed_cell["sheet"].capitalize()
                message = f"{sheet_name} sheet, Row {row_index}: {e}"
                error_list.append(message)
                material = None
            # If the material had a successful GET request, add properties, identifiers,
            # and select attributes as written in the excel
            else:

                material = copyMaterial(material, new_project, project)

                # Add properties,identifiers, and attributes to material
                for property in material_dict["properties"]:
                    material.add_property(property)
                for identifier in material_dict["identifiers"]:
                    material.add_identifier(identifier)
                for key_ in material_dict:
                    if key_ == "keywords":
                        if material.keywords is not None:
                            material.keywords += material_dict["keywords"]
                        else:
                            material.keywords = material_dict["keywords"]
                    elif key_ == "notes":
                        if material.notes is not None:
                            material.notes += material_dict["notes"]
                        else:
                            material.notes = material_dict["notes"]

        # create new material object otherwise
        else:
            material = _create_object(cript.Material, material_dict, parsed_cell)
        if material is not None:

            materials[key] = material
            if belongs_in_inv:
                if inventory_dict.get(cell_value, None):
                    inventory_dict[inv_name].append(material)
                else:
                    inventory_dict[inv_name] = [material]

    return materials, inventory_dict


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


def create_computation(
    parsed_computations, experiments, data, citations, software_configurations
):
    """Creates a dictionary of Computation objects based on the parsed inputs
    params:
    @parsed_computations dictionary of dictionaries containing information about computation objects
    @experiments dictionary of experiment objects
    @data dictionary of data objects
    @citations dictionary of citation objects
    @software_configurations dictionary of software configuration objects

    returns:
    dictionary of Computation objects
    """
    computations = {}

    for key, parsed_process in parsed_computations.items():
        comp_dict = {"conditions": [], "software_configurations": []}

        for parsed_cell in parsed_process.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                if cell_key == "citations":
                    pass
                else:
                    comp_dict[cell_key] = cell_value

            # Gets existing object if available
            elif cell_type == "relation":
                if cell_key == "experiment":
                    comp_dict["experiment"] = _get_relation(
                        experiments, cell_value, parsed_cell
                    )
                elif "software_configuration" in cell_key:
                    software_config = _get_relation(
                        software_configurations, cell_value, parsed_cell
                    )
                    if software_config:
                        comp_dict["software_configurations"].append(software_config)

            elif cell_type == "condition":
                condition = _create_condition(parsed_cell, data, citations)
                comp_dict["conditions"].append(condition)

        computation = _create_object(cript.Computation, comp_dict, parsed_cell)
        if computation is not None:
            computations[key] = computation

    return computations


def create_prerequisite_computation(parsed_prerequisites, computations):
    """Attaches prerequisite Computation  to a Computation node.
    params:
        parsed_...-dict of dicts
        processes-dict of objs

    returns:
        void
    """
    for key, parsed_prerequisite in parsed_prerequisites.items():
        for parsed_cell in parsed_prerequisite.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "relation":
                if cell_key == "computation":
                    computation = _get_relation(computations, cell_value, parsed_cell)

                elif cell_key == "prerequisite":
                    prerequisite = _get_relation(computations, cell_value, parsed_cell)

        if None not in (computation, prerequisite):
            computation.prerequisite_computation = prerequisite


def create_computational_process(
    parsed_comp_processes, experiments, software_configurations, data, citations
):
    """Creates a dictionary of Computational_process objects to be returned.
    params:
        @parsed_comp_processes dict of dict of computational process information
        @experiments -dict of Experiment objects
        @data dict of data objects
        @citations dict of citation objects
    returns
      dict of objects
    """
    comp_processes = {}

    for key, parsed_comp_process in parsed_comp_processes.items():
        comp_process_dict = {
            "properties": [],
            "conditions": [],
            "software_configurations": [],
        }

        for parsed_cell in parsed_comp_process.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                comp_process_dict[cell_key] = cell_value

            # Gets existing object if available
            elif cell_type == "relation":
                if cell_key == "experiment":
                    comp_process_dict["experiment"] = _get_relation(
                        experiments, cell_value, parsed_cell
                    )
                elif "software_configuration" in cell_key:
                    software_config = _get_relation(
                        software_configurations, cell_value, parsed_cell
                    )
                    if software_config:
                        comp_process_dict["software_configurations"].append(
                            software_config
                        )

            # Creates objects that will go into process node
            elif cell_type == "property":
                property = _create_property(parsed_cell, data, citations)
                comp_process_dict["properties"].append(property)

            elif cell_type == "condition":
                condition = _create_condition(parsed_cell, data, citations)
                comp_process_dict["conditions"].append(condition)

        comp_process = _create_object(
            cript.ComputationalProcess, comp_process_dict, parsed_cell
        )
        if comp_process is not None:
            comp_processes[key] = comp_process

    return comp_processes


def create_software_configuration(parsed_software, citations, project):
    """Creates a dictionary of Software_Configuration objects based on the parsed inputs
    params:
    @parsed_computations dictionary of dictionaries containing information about software configuration objects
    @citations dictionary of citation objects

    returns:
    dictionary of software_configuration objects
    """
    software_configurations = {}
    for key, parsed_process in parsed_software.items():
        config_dict = {
            "software": None,
            "algorithms": [],
        }  # dictionary for Software Configuartion object
        software_dict = {"group": project.group}  # dictionary for Software object
        for parsed_cell in parsed_process.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "attribute":
                if cell_key == "citations":
                    continue
                elif cell_key in {"name", "version", "source"}:
                    software_dict[cell_key] = cell_value
                elif cell_key == "notes":
                    config_dict[cell_key] = cell_value

            # create algorithm
            elif isinstance(cell_type, dict):

                if cell_type["type"] == "attribute":
                    alg_obj = create_algorithm(parsed_cell)
                    if alg_obj:
                        config_dict["algorithms"].append(alg_obj)

        software = _create_object(cript.Software, software_dict, parsed_cell)
        if software:
            try:
                software.save()
            except:
                software = cript.Software.get(
                    name=software_dict["name"],
                    version=software_dict["version"],
                )

        config_dict["software"] = software

        # Take algorithms out if none are present
        if not config_dict["algorithms"]:
            config_dict.pop("algorithms")

        software_configuration = _create_object(
            cript.SoftwareConfiguration, config_dict, parsed_cell
        )
        if software_configuration is not None:
            software_configurations[key] = software_configuration

    return software_configurations


def create_in_out_data_connections(
    parsed_in_out_data, computations, computational_processes, data
):
    """
    Attaches input and output data to a Computation or Computatinal Process object
    params:
        @parsed_in_out_data dict of dicts of information relating data to another node
        @computations dict of computation objects
        @computational_processes dict of computational process objects
    returns:
        void
    """
    merged_dict = (
        computations | computational_processes
    )  # merge dictionaries for ease of access

    for key, parsed_info in parsed_in_out_data.items():
        input_data = None
        output_data = None
        for parsed_cell in parsed_info.values():
            cell_type = parsed_cell["type"]
            cell_key = parsed_cell["key"]
            cell_value = parsed_cell["value"]

            if cell_type == "relation":
                if cell_key == "computation or computational process":
                    cript_obj = _get_relation(merged_dict, cell_value, parsed_cell)
                elif cell_key == "input data":
                    input_data = _get_relation(data, cell_value, parsed_cell)
                elif cell_key == "output data":
                    output_data = _get_relation(data, cell_value, parsed_cell)

        if None not in (cript_obj, input_data):
            cript_obj.input_data.append(input_data)
        if None not in (cript_obj, output_data):
            cript_obj.output_data.append(output_data)


def create_processes(parsed_processes, experiments, data, citations):
    """Creates a dictionary of Process objects to be returned.
    parsed_...-dict of objects
    experiments-dict of objects
    data-obj
    citations-list
    returns dict of objects"""
    processes = {}

    for key, parsed_process in parsed_processes.items():
        process_dict = {"properties": [], "conditions": []}

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


def create_prerequisite_process(parsed_prerequisites, processes):
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


def create_algorithm(parsed_cell):
    """
    Auxilliary function to abstract the creation of an Algorithm object with Parameters
    input:
    @parsed_cell dictionary of information about Algorithm
    returns:
    algorithm object or None

    """

    cell_type = parsed_cell["type"]
    cell_value = parsed_cell["value"]

    alg_dict = {"parameters": []}
    alg_dict["type"] = cell_type["value"]
    alg_dict["key"] = cell_value
    for key2, param in parsed_cell.items():
        if "parameter" in key2:
            param_dict = {}
            param_dict["key"] = param["value"]
            param_dict["value"] = param["input"]["value"]
            param_dict["unit"] = param.get("unit")
            param_object = _create_object(cript.Parameter, param_dict, parsed_cell)
            if param_object:
                alg_dict["parameters"].append(param_object)

    alg_obj = _create_object(cript.Algorithm, alg_dict, parsed_cell)
    return alg_obj


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
        # "method": None,
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

            elif cell_type == "method":
                if is_cell_true(parsed_cell["value"]):
                    property_dict["method"] = parsed_cell["key"]

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
        row_index = parsed_cell["index"] + row_input_can_start_from
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
        # Add 5 due to differences in DataFrame and Excel format
        row_index = parsed_cell["index"] + row_input_can_start_from
        sheet_name = parsed_cell["sheet"].capitalize()
        related_sheet = parsed_cell["key"].capitalize()
        value = parsed_cell["value"][0]
        message = f'{sheet_name} sheet, Row {row_index}: "{value}" does not exist in the {related_sheet} sheet.'
        error_list.append(message)
        return None


def is_cell_true(val):
    """Converts a cell value to a useable boolean"""
    return str(val).lower() != "false"


def copyMaterial(material, new_project, project):
    """
    Takes a material node and adjusts values to get rid of legacy code and incompatible features
    inputs:
    material - cript material node
    new_project - cript project node
    project - cript project node

    returns - cript material node
    """
    if new_project.name != project.name:
        # Sets new project and gets rid of url and uid to make new node object
        material.project = project
        material.url = None
        material.uid = None
        # Gets rid of citations that would cause permissions errors
        if material.group.name != project.group.name:
            for property in material.properties:
                property.citations = []
            material.group = project.group

    newProperties = []
    # Gets rid of any legacy properties/custom that won't upload
    for property in material.properties:
        if "+" not in property.key:
            newProperties.append(property)
    material.properties = newProperties

    return material

def create_computational_forcefield(parsed_cell):
    """
    Create a computational forcefield object
    param:
    @parsed_cell dictionary of information about object
    returns:
    Computational_forcefield object or None
    """
    # Try to assign all of computational_forcefield's attributes
    # Can't assign data and citation here
    building_block = (
        temp_dict.get("value")
        if (temp_dict := parsed_cell.get("building_block"))
        else None
    )
    coarse_grained_mapping = (
        temp_dict.get("value")
        if (temp_dict := parsed_cell.get("coarse_grained_mapping"))
        else None
    )
    implicit_solvent = (
        temp_dict.get("value")
        if (temp_dict := parsed_cell.get("implicit_solvent"))
        else None
    )
    source = (
        temp_dict.get("value") if (temp_dict := parsed_cell.get("source")) else None
    )
    description = (
        temp_dict.get("value")
        if (temp_dict := parsed_cell.get("description"))
        else None
    )

    object_dict = {
        "key": parsed_cell["value"],
        "building_block": building_block,
        "coarse_grained_mapping": coarse_grained_mapping,
        "implicit_solvent": implicit_solvent,
        "source": source,
        "description": description,
    }
    return _create_object(cript.ComputationalForcefield, object_dict, parsed_cell)

