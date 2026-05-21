import boto3
from config import BUCKET_NAME, DRY_RUN
from utils.logger import logger

s3 = boto3.client("s3")

# function receives dispute id as parameter, build s3 prefix with dispute id (dispute_id/), 
# create paginotr object to retrieve s3 objects. s3 returns max objects of 1000 per request, 
# paginator handles this by making multiple requests until all objects are retrieved. 
# start parginated s3 seach (10000 objects max per page), create list to hold results, 
# loop through parginated results (pages), store object keysin list and returns list object 
	
def list_s3_objects(dispute_id):
    prefix = f"{dispute_id}/"

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(
        Bucket=BUCKET_NAME, 
        Prefix=prefix
    )

    object_keys = []

    for page in pages:
        if "Contents" not in page:
            continue
        for obj in page["Contents"]:
            object_keys.append(obj["Key"])

    return object_keys

# function receives list of s3 object keys to delete, if list is empty return empty list, 
# create empty list to hold deleted objects, set batch size to 1000 (max allowed by s3 delete_objects API), 
# loop through object keys in batches of 1000, build delete payload with object keys

def delete_s3_objects(object_keys):
    if not object_keys:
        return []

    deleted = []
    batch_size = 1000

    for i in range(0, len(object_keys), batch_size):

        # Get the current batch of object keys (in batches of 1000) to delete
        batch = object_keys[i:i + batch_size]

        # creates s3 delete request body
        delete_payload = {
            "Objects": [{"Key": key} for key in batch]
        }

        if DRY_RUN:
            logger.info(f"DRY RUN - Would delete: {batch}")
            deleted.extend(batch)
            continue
        
        # Call S3 delete_objects API to delete the batch of objects 
        response = s3.delete_objects(
            Bucket=BUCKET_NAME,
            Delete=delete_payload
        )

        deleted_objects = response.get("Deleted", [])

        for obj in deleted_objects:
            deleted.append(obj["Key"])
            
    return deleted