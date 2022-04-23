import cript as C
from tqdm import tqdm
import traceback
from config import BASE_URL
from errors import GroupRelatedError
from cript.exceptions import (
    DuplicateNodeError,
    APIGetError,
)


def connect(token):
    """
    connect with backend service

    :return: backend service connection object
    :rtype: class:`cript.API`
    """
    return C.API(BASE_URL, token)


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
        group_obj = api.get(C.Group, {"name": group_name})
        return group_obj
    except APIGetError:
        raise GroupRelatedError(
            "Error: You must enter an existing CRIPT group. Try again."
        )


def get_collection(api, group_obj, coll_name):
    """
    search for existing collection_url, create collection if not exists

    :param api: api connection object
    :type api: class:`cript.API`
    :param group_obj: object of group
    :type group_obj: `cript.Group`
    :param coll_name: collection name
    :type coll_name: str
    :return: object of collection
    :rtype: `cript.Collection`
    """
    # Check if Collection exists
    try:
        collection_obj = api.get(
            C.Collection,
            {
                "group": group_obj.uid,
                "name": coll_name,
            },
        )
        return collection_obj
    except APIGetError:
        raise GroupRelatedError(
            "Error: You must enter an existing CRIPT collection. Try again."
        )


def upload(api, dict_, user_uid):
    """
    Save objects to database, update them if the object already exists
    dict: (name): (C.Base)
    """
    pbar = tqdm(
        total=len(dict_),
        mininterval=2,
        dynamic_ncols=True,
        bar_format="{l_bar}{bar}{r_bar}\n",
        unit="item",
        colour="GREEN",
    )
    for key, obj in dict_.items():
        try:
            api.save(obj)
        except DuplicateNodeError:
            query = {}
            for field in obj.unique_together:
                if field == "created_by":
                    query[field] = user_uid
                    continue

                value = obj.__dict__.get(field)
                if type(value) == type("a"):
                    query[field] = obj.__dict__.get(field)
                else:
                    query[field] = obj.__dict__.get(field).uid
            url = api.get(obj.__class__, query).url

            obj.url = url
            api.save(obj)
        except Exception:
            print(traceback.format_exc())
        finally:
            pbar.update(1)
    pbar.close()
