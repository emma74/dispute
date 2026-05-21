import json
import boto3

from datetime import datetime
from config import AUDIT_BUCKET
from utils.logger import logger

s3 = boto3.client("s3")

def upload_audit_log(audit_data):
    now = datetime.utcnow()

    timestamp = now.strftime("%Y%m%d-%H%M%S")
    
    key = (
        f"audit/year={now.year}/"
        f"month={now.month}/"
        f"purge-{timestamp}.json"
    )

    s3.put_object(
        Bucket=AUDIT_BUCKET,
        Key=key,
        Body=json.dumps(audit_data, indent=2),
        ContentType="application/json"
    )

    return key