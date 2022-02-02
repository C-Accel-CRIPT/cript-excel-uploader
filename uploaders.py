from bson.objectid import ObjectId
import time
import sys

import cript as C


def connect(db_username, db_password, db_project, db_database, user):
    return C.CriptDB(db_username, db_password, db_project, db_database, user)


def upload_group(db, group_name):
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
    # Check if Collection exists
    my_colls = db.view(C.Collection)
    for coll in my_colls:
        if coll["name"] == coll_name:
            coll_uid = str(coll["_id"])
            return coll_uid

    # Create Collection if it doesn't exist
    coll = C.Collection(coll_name)
    group = db.view(
        C.Group,
        {
            "scope": "all",
            "key": {"_id": ObjectId(group_uid)},
        },
    )[0]
    db.save(coll, group)

    return coll.uid


def upload_experiment(db, coll_uid, parsed_expts):
    expt_uids = {}
    for key in parsed_expts:
        # Create Experiment
        expt = C.Experiment(**parsed_expts[key])
        coll = db.view(
            C.Collection,
            {
                "scope": "all",
                "key": {"_id": ObjectId(coll_uid)},
            },
        )[0]
        db.save(expt, coll)

        expt_uids[key] = expt.uid

    return expt_uids


def _create_cond_list(db, parsed_conds, data_uids=None):
    """Create a list of Cond objects."""
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
                C.Data,
                {
                    "scope": "all",
                    "key": {"_id": ObjectId(datum_uid)},
                },
            )[0]
            cond.c_data.add(datum)

        conds.append(cond)

    return conds


def _create_prop_list(db, parsed_props, data_uids=None):
    """Create a list of Prop objects."""
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
                C.Data,
                {
                    "scope": "all",
                    "key": {"_id": ObjectId(datum_uid)},
                },
            )[0]
            prop.c_data.add(datum)

        # Add Cond objects
        if "cond" in parsed_props[prop_key]:
            parsed_conds = parsed_props[prop_key]["cond"]
            prop.cond = _create_cond_list(db, parsed_conds, data_uids)

        props.append(prop)

    return props


def upload_data(db, expt_uids, parsed_data):
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
            C.Experiment,
            {
                "scope": "all",
                "key": {"_id": ObjectId(expt_uid)},
            },
        )[0]

        db.save(datum, expt)

        data_uids[key] = datum.uid

    return data_uids


def upload_material(db, parsed_materials, data_uids, type, process_uids=None):
    material_uids = {}
    for parsed_material in parsed_materials.values():
        # Check if Material exists by CAS/Name combo
        if "cas" in parsed_material["iden"]:
            cas = parsed_material["iden"]["cas"]
            name = parsed_material["iden"]["name"]
            check = db.view(
                C.Material,
                {
                    "scope": "all",
                    "key": {"iden.0.cas": cas, "iden.0.name": name},
                },
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
                C.Process,
                {
                    "scope": "all",
                    "key": {"_id": ObjectId(process_uid)},
                },
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
                    "key": {"_id": ObjectId(reagent_uid)},
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
            C.Experiment,
            {
                "scope": "all",
                "key": {"_id": ObjectId(expt_uid)},
            },
        )[0]

        # Save Process to DB
        db.save(process, expt)

        process_uids[process_key] = process.uid

    return process_uids
