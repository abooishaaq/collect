import re

import forms
import schema
import query

from fastapi import FastAPI, HTTPException, BackgroundTasks

from engine import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_cockroachdb import run_transaction

import forms

app = FastAPI()




@app.post("/new-form")
async def create_form(form: schema.Form):
    for field in form.fields:
        print(field)
        if b"name" not in field:
            raise HTTPException(status_code=400, detail="field name missing")
        if b"type" not in field:
            raise HTTPException(status_code=400, detail="field name missing")
        if field[b"type"] not in [b"text", b"number"]:
            raise HTTPException(status_code=400, detail="invalid field type")

    res = run_transaction(sessionmaker(bind=engine),
                          lambda s: forms.create_form(s, form))

    if res is False:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    else:
        response = {}
        response["form_id"] = str(res["form_id"])
        response["fields"] = []
        for field in res["fields"]:
            response["fields"].append(
                {"id": field["id"], "name": field["name"]})
        return response


@app.post("/submit-form/")
async def submit_form(data: schema.FormData, bg_tasks: BackgroundTasks):
    sub_id = run_transaction(sessionmaker(bind=engine),
                    lambda s: forms.submit_form(s, data))
    
    bg_tasks.add_task(run_transaction(sessionmaker(bind=engine), lambda s: forms.call_webhook(s, data.form_id, sub_id)))

    return {"message": "Form submitted successfully."}


@app.post("/query/")
async def query_form(data: schema.QueryForm):
    parsed = query.parse_query(data.query)
    return run_transaction(sessionmaker(bind=engine),
                           lambda s: parsed.execute(s))


@app.post("/webhook/")
async def set_webhook(data: schema.WebhookData):
    url = data.url
    # https://stackoverflow.com/questions/60674474/complete-regex-to-match-url-with-port-number
    res = re.search(
        r"https?:\/\/(?:w{1,3}\.)?[^\s.]+(?:\.[a-z]+)*(?::\d+)?(?![^<]*(?:<\/\w+>|\/?>))", url)
    if res is None:
        raise HTTPException(400, detail="url is incorrect")
    return run_transaction(sessionmaker(bind=engine),
                           lambda s: forms.create_webhook(s, data))

