import cript as C

# Configs
BASE_URL = "https://criptapp.herokuapp.com/api/"
TOKEN = ""  # Your Token
PUBLIC_FLAG = True  # Set the flag to true to make your data go public
# GROUP_URL = "https://criptapp.herokuapp.com/api/group/5/"
# COLLECTION_URL = "https://criptapp.herokuapp.com/api/collection/7/"

FILE_PATH = r"C:\Users\Orange Meow\Desktop\MIT CRIPT\excel_uploader\excel template\test files\file1.txt"

# Server Connection
db = C.API(BASE_URL, TOKEN)

# Group, Collection and Experiment
group_name = "test_group"
collection_name = "excel_uploader_test0303"
experiment_name = ""


# Helper methods
def _get_id_from_url(url: str):
    _id = url.rstrip("/").split("/")[-1]
    return int(_id)


# Search for Group, Collection and Experiment
group_search_result = db.search(C.Group, {"name": group_name})
GROUP_URL = group_search_result["results"][0]["url"]
group_obj = db.get(GROUP_URL)


collection_search_result = db.search(
    C.Collection,
    {
        "name": collection_name,
        "group": _get_id_from_url(GROUP_URL),
    },
)
COLLECTION_URL = collection_search_result["result"][0]["url"]
collection_obj = db.get(COLLECTION_URL)

experiment_search_result = db.search(
    C.Experiment,
    {
        "name": experiment_name,
        "group": _get_id_from_url(GROUP_URL),
    },
)
EXPERIMENT_URL = experiment_search_result["result"][0]["url"]
experiment_obj = db.get(EXPERIMENT_URL)


data_search_result = db.search(
    C.Data,
    {
        "group": _get_id_from_url(group_obj.url),
        "experiment": _get_id_from_url(experiment_obj.url),
        "name": "Crude SEC of polystyrene",
    },
)

if data_search_result["count"] == 0:
    # Create Data and File Object
    data_obj = C.Data(
        group=group_obj,
        experiment=experiment_obj,
        name="Crude SEC of polystyrene",
        type="sec",
        sample_prep="test prep",
        public=PUBLIC_FLAG,
    )
    db.save(data_obj)
    print("Data Node Saved")
else:
    data_url = data_search_result["results"][0]["url"]
    data_obj = db.get(data_url)

file_obj = C.File(
    group=group_obj,
    data=data_obj,
    source=FILE_PATH,
    public=PUBLIC_FLAG,
)
db.save(file_obj)
print("File Node Saved")

data_obj.add_file(file_obj)
db.save(data_obj)
print("Data Node Updated")

# search for result
material_search_result = db.search(
    C.Material,
    {
        "group": _get_id_from_url(GROUP_URL),
        "name": "polystyrene",
    },
)  # You may add more fields to the query
if material_search_result["count"] == 0:
    print("Material Not Found,Raise an error")
material_url = material_search_result["results"][0]["url"]  # First result
material_obj = db.get(material_url)
print("Material Node Found")

# add properties to material
property_obj = C.Property(key="mw_n", value=4800, unit="g/mol")
property_obj.add_data(data_obj)
material_obj.add_property(property_obj)
db.save(material_obj)
print("Material Node Saved")
