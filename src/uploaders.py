import cript as C
from tqdm import tqdm
import traceback

from cript.exceptions import (
    DuplicateNodeError,
    APIGetError,
)


def connect(base_url, token):
    """
    connect with backend service

    :return: backend service connection object
    :rtype: class:`cript.API`
    """
    return C.API(base_url, token)


def get_group(api, group_name):
    """
    search for existing group_url

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_name: group name
    :type group_name: str
    :return: group object
    :rtype: `cript.Group`
    """
    # Check if Group exists
    try:
        group_obj = api.get(
            C.Group,
            {"name": group_name},
            max_level=0,
        )
        return group_obj
    except APIGetError:
        raise Exception(
            "Error: You must enter " "an existing CRIPT group. " "Try again."
        )


def get_collection(api, group_obj, collection_name):
    """
    search for existing collection_url, create collection if not exists

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.Group`
    :param collection_name: collection name
    :type collection_name: str
    :return: object of collection
    :rtype: `cript.Collection`
    """
    # Check if Collection exists
    try:
        collection_obj = api.get(
            C.Collection,
            {
                "group": group_obj.uid,
                "name": collection_name,
            },
            max_level=0,
        )
        return collection_obj
    except APIGetError:
        raise Exception(
            "Error: You must enter " "an existing CRIPT collection. " "Try again."
        )


def upload(api, node_type, dict_, user_uid):
    """
    Save objects to database, update them if the object already exists
    dict: (name): (C.Base)
    """
    if len(dict_) == 0:
        return 0
    pbar = tqdm(
        total=len(dict_),
        mininterval=0.1,
        dynamic_ncols=True,
        desc=f"Uploading {node_type}: ",
        unit="item",
    )
    for key, obj in dict_.items():
        try:
            api.save(obj)
        except DuplicateNodeError:
            query = {}
            for field in obj.unique_together:
                if field == "created_by":
                    query["created_by"] = user_uid
                    continue

                value = getattr(obj, field)
                if isinstance(value, str):
                    query[field] = value
                else:
                    query[field] = value.uid
            try:
                raw_obj = api.get(obj.__class__, query)
                if obj.node_name == "File":
                    for data_obj in raw_obj.data:
                        obj.data.append(data_obj)

                obj.url = raw_obj.url
                api.save(obj)
            except Exception as e:
                print(
                    f"\nSave {obj.node_name} Failed, "
                    f"Node object: {obj}, "
                    f"Error Info: {e.__str__()}."
                )
                print(traceback.format_exc())
        except Exception as e:
            print(
                f"\nSave {obj.node_name} Failed, "
                f"Node object: {obj}, "
                f"Error Info: {e.__str__()}."
            )
            # print(traceback.format_exc())
        finally:
            pbar.update(1)
    pbar.close()
