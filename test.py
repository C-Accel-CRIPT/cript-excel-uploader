import uploaders

db = uploaders.connect()
print(db.get("https://criptapp.herokuapp.com/api/identity/4/"))
