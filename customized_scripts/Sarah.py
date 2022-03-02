import cript as C

# Configs
BASE_URL = "https://criptapp.herokuapp.com/api/"
TOKEN = "Token 51ed84aeb0d85910cf992133e6dac3f2788c1486"
GROUP_URL = "https://criptapp.herokuapp.com/api/group/5/"
COLLECTION_URL = "https://criptapp.herokuapp.com/api/collection/7/"
EXPERIMENT_URL = "https://criptapp.herokuapp.com/api/experiment/93/"

FILE_PATH = r"C:\Users\Orange Meow\Desktop\MIT CRIPT\excel_uploader\excel template\test files\file1.txt"

# Server Connection
db = C.API(BASE_URL, TOKEN)
group_obj = db.get(GROUP_URL)
collection_obj = db.get(COLLECTION_URL)
experiment_obj = db.get(EXPERIMENT_URL)

# Create Data and File Object
data_obj = C.Data(
    group=group_obj,
    experiment=experiment_obj,
    name="Crude SEC of polystyrene",
    type="sec",
    sample_prep="test prep",
)
db.save(data_obj)
print("Data Node Saved")

file_obj = C.File(group=group_obj, data=data_obj, source=FILE_PATH)
db.save(file_obj)
print("File Node Saved")

data_obj.add_file(file_obj)
db.save(data_obj)
print("Data Node Updated")

# search for result
material_search_result = db.search(
    C.Material, {"name": "polystyrene"}
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
