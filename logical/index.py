
import json


data = '{ "name": "John", "age": 30, "city": "New York" }'
result = json.loads(data)
print(result["name"])  # Output: John