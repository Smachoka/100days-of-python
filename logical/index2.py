import json

data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}
data = json.dumps(data, indent=4)
print(data)
print(json.dumps(42))