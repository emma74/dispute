import json
from datetime import datetime

from utils.logger import logger
from services.db_service import get_dispute_ids
from services.s3_service import list_s3_objects, delete_s3_objects
from services.audit_service import upload_audit_log


def lambda_handler(event, context):

    execution_time = datetime.utcnow().isoformat()
    audit_results = []
    total_deleted = 0

    try:
        dispute_ids = get_dispute_ids()
        logger.info(f"Retrieved {len(dispute_ids)} dispute IDs")

        for dispute_id in dispute_ids:

            result = {
                "disputeId": dispute_id,
                "status": "",
                "deletedObjects": [],
                "deletedCount": 0,
                "error": None
            }

            try:
                object_keys = list_s3_objects(dispute_id)

                if not object_keys:
                    result["status"] = "NO_OBJECTS_FOUND"
                    audit_results.append(result)
                    continue

                deleted_objects = delete_s3_objects(object_keys)

                result["status"] = "SUCCESS"
                result["deletedObjects"] = deleted_objects
                result["deletedCount"] = len(deleted_objects)

                total_deleted += len(deleted_objects)

            except Exception as e:
                logger.exception(f"Failed processing dispute {dispute_id}")
                result["status"] = "FAILED"
                result["error"] = str(e)

            audit_results.append(result)

        audit_document = {
            "executionTime": execution_time,
            "totalDisputesProcessed": len(dispute_ids),
            "totalObjectsDeleted": total_deleted,
            "results": audit_results
        }

        audit_key = upload_audit_log(audit_document)
        logger.info(f"Audit uploaded: {audit_key}")

        return {
            "statusCode": 200,
            "body": json.dumps(audit_document)
        }

    except Exception as e:
        logger.exception("Fatal execution failure")

        return {
            "statusCode": 500,
            "body": str(e)
        }