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
    :param base_url: host domain
    :param token: authentication token
    :return: backend service connection object
    :rtype: class:`cript.API`
    """
    return C.API(base_url, token)


def get_group(api, group_name):
    """
    Search for group with same group_name in db
    Create group object if exists

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
            f"Error: You are not in group [{group_name}].\n"
            f"You may enter a wrong group name "
            f"or you are not a member of the group. "
            f"Have a check."
        )


def get_collection(api, group_obj, collection_name):
    """
    Search for collection with same collection_name in the group
    Create collection object if exists

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
            f"Error: You don't have collection [{collection_name}].\n"
            f"You may enter a wrong collection name "
            f"or you forget to create the collection. "
            f"Have a check."
        )


def upload(api, node_type, dict_, user_uid):
    """
    Save objects to database, update them if the object already exists
    :param api: cript api connection
    :type api: cript.API
    :param node_type: the type of current nodes to be uploaded
    :type node_type: str
    :param dict_: a dictionary of nodes, (name): (C.Base)
    :type dict_: dict
    :param user_uid: uid of current user
    :type user_uid: str
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
                    f"\nSave [{node_type}] Failed, "
                    f"Node object: {obj}, "
                    f"Error Info: {e.__str__()}.",
                    end="",
                )
                print(traceback.format_exc())
        except Exception as e:
            print(
                f"\nSave [{node_type}] Failed, "
                f"Node object: {obj}, "
                f"Error Info: {e.__str__()}.",
                end="",
            )
        finally:
            pbar.update(1)
    pbar.close()
