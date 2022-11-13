import re
from typing import Type
from model import Field, FieldType, ResponseNumber, ResponseText, Submission
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException


class Query:
    qtype = str
    form_id = None
    submission_id = None
    fields = []
    feildToRegex = {}

    def __init__(self, form_id, submission_id, fields, feildToRegex):
        self.form_id = form_id
        self.submission_id = submission_id
        self.fields = fields
        self.feildToRegex = feildToRegex

    def execute(self, session: Type[sessionmaker]):
        submission = None
        if self.submission_id is not None:
            submission = session.query(Submission).filter(
                Submission.id == self.submission_id).first()
            self.form_id = session.query(Submission).filter(
                Submission.id == submission.id).first().form_id
        text_fields = session.query(Field).filter(
            Field.form_id == self.form_id and Field.id.in_(tuple(self.fields)) and Field.type.in_((FieldType.text))).all()
        num_fields = session.query(Field).filter(
            Field.form_id == self.form_id and Field.id.in_(tuple(self.fields)) and Field.type.in_((FieldType.number))).all()

        data = {}  # {submission_id: {field_id: response}}

        def process_resps(resps):
            for r in resps:
                if r.submission_id not in data:
                    data[r.submission_id] = {}
                data[r.submission_id][r.field_id] = r.response

        for field in text_fields:
            resps = session.query(ResponseText).filter(
                ResponseText.field_id == field.id).all()
            process_resps(resps)
        for field in num_fields:
            resps = session.query(ResponseNumber).filter(
                ResponseNumber.field_id == field.id).all()
            process_resps(resps)
        
        # check regex

        for subid in data.keys():
            sub = data[subid]
            print(sub)
            for k in sub.keys():
                v = sub[k]
                if k in self.feildToRegex:
                    if re.search(self.feildToRegex[k], v) is None:
                        del data[subid]
                        break

        # print(data)
    
        return data


def parse_query(query: str):
    print("parsing query ", query)
    # between () is the form id
    form_id_r = re.search(r"\((.+)\)", query)
    submittion_id_r = re.search(r"\'(.+)'", query)
    if form_id_r is None and submittion_id_r is None:
        raise HTTPException(status_code=400, detail="Invalid query")
    form_id = form_id_r.group(1) if form_id_r is not None else None
    submittion_id = submittion_id_r.group(
        1) if submittion_id_r is not None else None
    # between [] is the fields
    fields_r = re.search(r"\[(.+)\]", query)
    if fields_r is None:
        raise HTTPException(status_code=400, detail="No fields found")
    fields = list(map(lambda x: x.strip(), fields_r.group(1).split(",")))
    print("fields ", fields)
    regexes_r = re.search(r"\{(.+)\}", query)
    fieldToRegex = {}
    if regexes_r is not None:
        # between {} is the regex
        regexes = map(lambda x: x.strip(), regexes_r.group(1).split(","))
        for r in regexes:
            # split at =
            r = r.split("=")
            # remove space
            r[0] = r[0].strip()
            r[1] = r[1].strip()
            fieldToRegex[r[0]] = re.compile(r[1])
    print("field to regexes ", fieldToRegex)
    return Query(form_id, submittion_id, fields, fieldToRegex)
