import schema
import requests
import query

from typing import Type
from engine import engine
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from model import Form, Field, FieldType, ResponseNumber, ResponseText, Submission, WebHook
from sqlalchemy_cockroachdb import run_transaction


def call_webhook(session: Type[sessionmaker], form_id: str, sub_id: str):
    webhooks = session.query(WebHook).filter(WebHook.form_id == form_id).all()
    wbhooks = [[webhook.url, webhook.query] for webhook in webhooks]

    async def webhook_caller():
        print("calling webhooks")
        for webhook in wbhooks:
            print("webhok url: ", webhook)
            try:
                result = None
                if webhook[1] is not None:
                    parsed = query.parse_query(webhook[1])
                    parsed.submission_id = sub_id
                    result = run_transaction(sessionmaker(
                        bind=engine), lambda s: parsed.execute(s))
                requests.post(webhook[0], json={
                              "submission_id": str(sub_id), "result": result})
            except Exception as e:
                print(e)
                print("failed to post to the webhook")
    return webhook_caller


def create_form(session: Type[sessionmaker], form: schema.Form):
    form_ = Form(
        name=form.name, description=form.description)
    session.add(form_)
    session.flush()
    try:
        session.refresh(form_)
    except Exception as e:
        print(e)
        return False
    print(form_.id)
    resp = {}  # {field_name: field_id}
    resp["form_id"] = form_.id
    resp["fields"] = []
    fields = []
    for f in form.fields:
        field = Field(
            name=str(f[b"name"], "utf-8"),
            type=f[b"type"] == "text" and 1 or 2,
            form_id=form_.id
        )
        session.add(field)
        fields.append(field)
    session.flush()
    for field in fields:
        try:
            session.refresh(field)
            resp["fields"].append({"id": field.id, "name": field.name})
        except Exception as e:
            print(e)
            return False

    print(f"Created form with id {form_.id} and fields {resp['fields']}")
    return resp


def submit_form(session: Type[sessionmaker], data: schema.FormData):
    form = session.query(Form).filter(Form.id == data.form_id).first()
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")

    submission = Submission(form_id=data.form_id)
    session.add(submission)
    session.flush()
    session.refresh(submission)

    for field_id, response in data.data.items():
        field_text = session.query(Field).filter(
            Field.id == field_id and Field.type.in_((FieldType.text))).first()
        field_number = session.query(Field).filter(
            Field.id == field_id and Field.type.in_((FieldType.number))).first()
        if field_text is not None:
            response_text = ResponseText(
                submission_id=submission.id, field_id=field_id, form_id=data.form_id, response=response)
            session.add(response_text)
        elif field_number is not None:
            response_number = ResponseNumber(
                submission_id=submission.id, field_id=field_id, form_id=data.form_id, response=response)
            session.add(response_number)
        else:
            raise HTTPException(status_code=404, detail="Field not found")

    session.flush()
    session.refresh(submission)

    return submission.id


def create_webhook(session: Type[sessionmaker], webhook: schema.WebhookData):
    form_id = None
    if webhook.query is not None:
        parsed = query.parse_query(webhook.query)
        form_id = parsed.form_id
    else:
        form_id = webhook.form_id

    if form_id is None:
        raise HTTPException(400, "no valid form id found")

    form = session.query(Form).filter(Form.id == form_id).first()
    if form is None:
        raise HTTPException(status_code=404, detail="Form not found")

    webhook_ = WebHook(
        form_id=form_id, url=webhook.url, query=webhook.query)
    session.add(webhook_)
    session.flush()
