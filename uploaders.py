from bson.objectid import ObjectId
import time
import sys

import cript as C


def connect(db_username, db_password, db_project, db_database, user):
    """
    connect with Mongodb database
    (WARNING: will migrate to Postgre soon)
    :param db_username: database username
    :type db_username: str
    :param db_password: database password
    :type db_password: str
    :param db_project: database project name
    :type db_project: str
    :param db_database: database name
    :type db_database: str
    :param user: user email address
    :type user: str
    :return: database connection object
    :rtype: class:`cript.CriptDB`
    """
    return C.CriptDB(db_username, db_password, db_project, db_database, user)


def upload_group(db, group_name):
    """
    search for existing group_uid
    (WARNING: db.view() has a default return limit of 50)
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param group_name: group name
    :type group_name: str
    :return: unique id of group
    :rtype: str
    """
    # Check if Group exists
    my_groups = db.view(C.Group)
    for group in my_groups:
        if group["name"] == group_name:
            group_uid = str(group["_id"])
            return group_uid

    # # Create group if it doesn't exist
    # group = C.Group(group_name)

    # try:
    #     db.save(group)
    # except ValueError as e:
    #     print(f"ValueError when saving '{group.name}' group: {e}\nContinuing anyways...")

    # return group.uid

    # Temp solution while group creation is broken
    print("\nError: You must enter an existing CRIPT group. Try again.\n")
    time.sleep(5)
    sys.exit(1)


def upload_collection(db, group_uid, coll_name):
    """
    search for existing collection_uid, create collection if not exists
    (WARNING: db.view() has a default return limit of 50)
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param group_uid: unique id for group
    :type group_uid: str
    :param coll_name: collection name
    :type coll_name: str
    :return: unique id of collection
    :rtype: str
    """
    # Check if Collection exists
    my_colls = db.view(C.Collection)
    for coll in my_colls:
        if coll["name"] == coll_name:
            coll_uid = str(coll["_id"])
            return coll_uid

    # Create Collection if it doesn't exist
    coll = C.Collection(coll_name)
    group = db.view(C.Group, {"scope": "all", "key": {"_id": ObjectId(group_uid)}})[0]
    db.save(coll, group)

    return coll.uid


def upload_experiment(db, coll_uid, parsed_expts):
    """
    upload the experiment data and return unique id of experiment
    (WARNING: db.view() is taking all of the data in the collection out.
    It also has a default return limit of 50)
    (WARNING: currently only add supported, so there'll be duplicated data)
    (TBC: make an update on last_modified_date once update is supported)
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param coll_uid: unique id of collection
    :type coll_uid: str
    :param parsed_expts: parsed data of experiments (experiment_sheet.parsed)
    :type parsed_expts: dict
    :return: a dict contains (experiment name) : (unique id of experiment) pair
    :rtype: dict
    """
    expt_uids = {}
    for key in parsed_expts:
        # Create Experiment
        expt = C.Experiment(**parsed_expts[key])
        coll = db.view(
            C.Collection, {"scope": "all", "key": {"_id": ObjectId(coll_uid)}}
        )[0]

        # Collection is the parent key of experiment, we need to update collection
        # when a new experiment is added.
        db.save(expt, coll)

        expt_uids[key] = expt.uid

    return expt_uids


def _create_cond_list(db, parsed_conds, data_uids=None):
    """
    Create a list of Cond objects.
    Used in Material,Process and Data
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param parsed_conds: dict contains (cond) : (value dict) pair (eg.'temp': {'data': {}, 'value': 2, 'unit': 'degC'})
    :type parsed_conds: dict
    :param data_uids: dict contains (name) : (data_uid) pair
    :type data_uids: dict
    :return: list of dicts of condition pair
            (eg.[{ "uncer": null, "key": "temp", "c_data": [], "value": "2 degree_Celsius"}]
    :rtype: list
    """
    conds = []
    for cond_key in parsed_conds:
        # Create Cond object
        if "unit" in parsed_conds[cond_key]:
            cond = C.Cond(
                key=cond_key,
                value=parsed_conds[cond_key]["value"]
                * C.Unit(parsed_conds[cond_key]["unit"]),
            )
        else:
            cond = C.Cond(key=cond_key, value=parsed_conds[cond_key]["value"])

        # Add Data object
        parsed_datum = parsed_conds[cond_key]["data"]

        if len(parsed_datum) > 0:
            datum_uid = data_uids[parsed_datum]
            datum = db.view(
                C.Data, {"scope": "all", "key": {"_id": ObjectId(datum_uid)}}
            )[0]
            cond.c_data.add(datum)

        conds.append(cond)

    return conds


def _create_prop_list(db, parsed_props, data_uids=None):
    """
    Create a list of Prop objects.
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param parsed_props: a dict contains parsed properties
    :type parsed_props: dict
    :param data_uids: dict contains (name) : (data_uid) pair
    :type data_uids: dict
    :return: a list of class: `cript.Prop` objects
    :rtype: list
    """
    props = []
    for prop_key in parsed_props:
        attrs = parsed_props[prop_key]["attr"]

        # Create Prop object
        if "unit" in parsed_props[prop_key]:
            prop = C.Prop(
                key=prop_key,
                value=parsed_props[prop_key]["value"]
                * C.Unit(parsed_props[prop_key]["unit"]),
                **attrs,
            )
        else:
            prop = C.Prop(key=prop_key, value=parsed_props[prop_key]["value"], **attrs)

        # Add Data object
        parsed_datum = parsed_props[prop_key]["data"]

        if len(parsed_datum) > 0:
            datum_uid = data_uids[parsed_datum]
            datum = db.view(
                C.Data, {"scope": "all", "key": {"_id": ObjectId(datum_uid)}}
            )[0]
            prop.c_data.add(datum)

        # Add Cond objects
        if "cond" in parsed_props[prop_key]:
            parsed_conds = parsed_props[prop_key]["cond"]
            prop.cond = _create_cond_list(db, parsed_conds, data_uids)

        props.append(prop)

    return props


def upload_data(db, expt_uids, parsed_data):
    """
    upload data to the database and return a dict of name:data_uid pair
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param expt_uids: (name) : (unique id of experiment) pair
    :type expt_uids: dict
    :param parsed_data: parsed data of data_sheet.parsed (data_sheet.parsed)
    :type parsed_data: dict
    :return: (name) : (unique id of data) pair
    :rtype: dict
    """
    # updateByPrimaryKey(name)
    data_uids = {}
    for key in parsed_data:
        parsed_datum = parsed_data[key]

        file = C.File(**parsed_datum["file"])
        datum = C.Data(file=file, **parsed_datum["base"])

        # Add Cond objects
        parsed_conds = parsed_datum["cond"]
        datum.cond = _create_cond_list(db, parsed_conds)

        # Grab Experiment
        expt_uid = expt_uids[parsed_datum["expt"]]
        expt = db.view(
            C.Experiment, {"scope": "all", "key": {"_id": ObjectId(expt_uid)}}
        )[0]

        db.save(datum, expt)

        data_uids[key] = datum.uid

    return data_uids


def upload_material(db, parsed_materials, data_uids, type, process_uids=None):
    """
    upload material to the database and return a dict of name:material_uid pair
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param parsed_materials: reagent_sheet.parsed or product_sheet.parsed
    :type parsed_materials: dict
    :param data_uids: (name) : (unique id of data) pair
    :type data_uids: dict
    :param type: ?
    :type type: ?
    :param process_uids: (name) : (unique id of process) pair
    :type process_uids: dict
    :return: (name) : (unique id of material) pair
    :rtype: dict
    """
    material_uids = {}
    for parsed_material in parsed_materials.values():
        # Check if Material exists by CAS/Name combo
        if "cas" in parsed_material["iden"]:
            cas = parsed_material["iden"]["cas"]
            name = parsed_material["iden"]["name"]
            check = db.view(
                C.Material,
                {"scope": "all", "key": {"iden.0.cas": cas, "iden.0.name": name}},
            )
            if len(check) > 0:
                # Add Material object to materials dict
                material_uids[name] = str(check[0]["_id"])
                continue

        # Create Material object
        iden = C.Iden(**parsed_material["iden"])
        material = C.Material(iden=iden, **parsed_material["base"])

        # Handle 'process' field
        if "process" in parsed_material and process_uids is not None:
            process_uid = process_uids[parsed_material["process"]]
            process = db.view(
                C.Process, {"scope": "all", "key": {"_id": ObjectId(process_uid)}}
            )[0]
            material.c_process.add(process)

        # Add Prop objects
        parsed_props = parsed_material["prop"]
        if len(parsed_props) > 0:
            material.prop = _create_prop_list(db, parsed_props, data_uids)

        # Add Cond objects
        parsed_conds = parsed_material["cond"]
        if len(parsed_conds) > 0:
            material.storage = _create_cond_list(db, parsed_conds, data_uids)

        # Save material to DB
        try:
            db.save(material)
        except AttributeError as e:
            print(
                f"AttributeError when saving '{material.name}': {e}\nContinuing anyways..."
            )

        # Add saved Material object to materials dict
        material_uids[material.name] = material.uid

    return material_uids


def upload_process(
    db, expt_uids, parsed_ingrs, parsed_processes, reagent_uids, data_uids
):
    """
    upload process to the database and return a dict of name:process_uid pair
    :param db: database connection object
    :type db: class:`cript.CriptDB`
    :param expt_uids: (name) : (unique id of experiment) pair
    :type expt_uids: dict
    :param parsed_ingrs: ingr_sheet.parsed
    :type parsed_ingrs: dict
    :param parsed_processes: process_sheet.parsed
    :type parsed_processes: dict
    :param reagent_uids: (name) : (unique id of material) pair
    :type reagent_uids: dict
    :param data_uids: (name) : (unique id of data) pair\
    :type data_uids: dict
    :return: (name) : (unique id of process) pair
    :rtype: dict 
    """
    process_uids = {}
    for process_key in parsed_processes:
        parsed_process = parsed_processes[process_key]

        # Generate ingr list
        ingr = []
        process_ingr = parsed_ingrs[process_key]
        for ingr_key in process_ingr:
            # Define reagent
            reagent_uid = reagent_uids[ingr_key]
            reagent = db.view(
                C.Material,
                {
                    "scope": "all",
                    "key": {
                        "_id": ObjectId(reagent_uid),
                    },
                },
            )

            if len(reagent) > 0:
                reagent = reagent[0]

            # Append material to ingr list
            ingr.append([reagent])

            # Append quantity to ingr list
            qty = process_ingr[ingr_key]["quantity"]
            qty_key = list(qty)[0]
            qty_value = qty[qty_key]["value"]
            qty_unit = qty[qty_key]["unit"]
            ingr[-1].append(qty_value * C.Unit(qty_unit))

            # Append keyword to ingr list
            ingr[-1].append(process_ingr[ingr_key]["keyword"])

        # Create Process object
        process = C.Process(ingr=ingr, **parsed_processes[process_key]["base"])

        # Add Prop objects
        parsed_props = parsed_process["prop"]
        if len(parsed_props) > 0:
            process.prop = _create_prop_list(db, parsed_props, data_uids)

        # Add Cond objects
        parsed_conds = parsed_process["cond"]
        if len(parsed_conds) > 0:
            process.cond = _create_cond_list(db, parsed_conds, data_uids)

        # Grab Experiment
        expt_uid = expt_uids[parsed_process["expt"]]
        expt = db.view(
            C.Experiment, {"scope": "all", "key": {"_id": ObjectId(expt_uid)}}
        )[0]

        # Save Process to DB
        db.save(process, expt)

        process_uids[process_key] = process.uid

    return process_uids
