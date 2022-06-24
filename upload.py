import cript

from tqdm import tqdm


def upload(api, obj_dict, obj_type):
    # Instantiate progress bar
    pbar = tqdm(
        total=len(obj_dict),
        mininterval=0.1,
        dynamic_ncols=True,
        desc=f"Uploading {obj_type} objects: ",
        unit="item",
    )

    for key, obj in obj_dict.items():
        try:
            api.save(obj)
        except cript.exceptions.DuplicateNodeError as e:
            # Get values for the object's unique fields
            unique_together = {}
            for field in obj.unique_together:
                if field == "created_by":
                    value = api.user.uid
                else:
                    value = getattr(obj, field)
                    if hasattr(value, "uid"):
                        value = value.uid
                unique_together[field] = value

            # Update existing object by swapping URLs
            existing_obj = api.get(obj.__class__, unique_together, max_level=0)
            obj.url = existing_obj.url
            api.save(obj)
            obj_dict[key] = existing_obj
        finally:
            pbar.update(1)  # Increment progress bar

    pbar.close()
