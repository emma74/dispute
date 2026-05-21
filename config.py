import os

BUCKET_NAME = os.environ["BUCKET_NAME"]

AUDIT_BUCKET = os.environ["AUDIT_BUCKET"]

CUTOFF_DATE = os.environ["CUTOFF_DATE"]

SECRET_ID = os.environ["SECRET_ID"]

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"