import json
import requests
import uvicorn

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# ensure that app is running at port 8000

url = "http://localhost:8000"


response = requests.post(f"{url}/new-form/", json={
    "name": "My Form",
    "description": "My Form Description",
    "fields": [
        {
            "name": "name",
            "type": "text"
        },
        {
            "name": "email",
            "type": "text"
        },
        {
            "name": "phone",
            "type": "text"
        }
    ]
})

print("created a new form")
print("response:")
print(response.text)

form_info = json.loads(response.text)

form_fields_info = {}
for field in form_info["fields"]:
    form_fields_info[field["name"]] = field["id"]

print(form_fields_info)

fake_data = [{
    "name": "John Doe",
    "email": "johndoe@gmail.com",
    "phone": "+91 95658 27456"
},
    {
    "name": "Joe Doe",
    "email": "joedoe@cmail.com",
    "phone": "+91 97456 95658"
}]

form_data = {}
form_data["form_id"] = form_info["form_id"]

fields = ",".join(form_fields_info.values())
form_id = form_info["form_id"]

response = requests.post(f"{url}/webhook/", json={
    "url": "http://localhost:3000/",
    "form_id": form_id
})

print(response.text)

for fake in fake_data:
    form_data["data"] = {}
    for k, v in fake.items():
        form_data["data"][form_fields_info[k]] = v
    response = requests.post(f"{url}/submit-form", json=form_data)
    print(response.text)


print("querying data")

regexes = f"{fields[1]} = gmail"

response = requests.post(
    f"{url}/query", json={"query": "({form_id}) [{fields}] {{ {regexes} }}".format(form_id=form_id, fields=fields, regexes=regexes)})

print(response.text)
