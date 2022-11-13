import os
import model

from sqlalchemy import create_engine

db_uri = os.environ["DATABASE_URL"]

if __name__ == "__main__":
    try:
       engine = create_engine(db_uri)
    except Exception as e:
        print("Failed to connect to database.")
        print(f"{e}")
        exit(1)

    model.Form.metadata.create_all(engine)
    model.Field.metadata.create_all(engine)
    model.Query.metadata.create_all(engine)
    model.Meta.metadata.create_all(engine)
    model.Submission.metadata.create_all(engine)
    model.ResponseText.metadata.create_all(engine)
    model.ResponseNumber.metadata.create_all(engine)
    model.WebHook.metadata.create_all(engine)
