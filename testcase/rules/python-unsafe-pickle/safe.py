import json


serialized_data = input("JSON data: ")
value = json.loads(serialized_data)

print(value)

