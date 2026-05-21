import json
import boto3
import pymssql

from config import SECRET_ID, CUTOFF_DATE

secrets_client = boto3.client("secretsmanager")


def get_db_credentials():

    # returns a dict including SecretString key:value pairs 
    response = secrets_client.get_secret_value(SecretId=SECRET_ID)

    # convert SecretString key:value pairs from JSON string to dict and return
    return json.loads(response["SecretString"])
    

# function creates and return connection to SQL server using pyodbc 
# function retrieves DB credentials from AWS Secrets Manager, build SQL connection string, 
# opens DB connection and returns connection object 
def get_db_connection():
    creds = get_db_credentials()

    conn = pymssql.connect(
        server=creds["host"],
        port=int(creds["port"]),
        user=creds["username"],
        password=creds["password"],
        database="Application"

    )

    return conn

# function query returns dispue IDs belonging to deleted merchants 
# DisputeIDs are converted to lowercase because S3 object keys are all lowercase 
# This ensures we can find the correct objects to delete. Calls get_db_connection(), 
# returns pymssql object (conn), create cursor with conn object, executes query 
# with CUTOFF_DATE parameter, fetches all rows, extracts dispute IDs to a list, 
# closes connection and returns list of dispute IDs.

def get_dispute_ids():
    query = """
    SELECT LOWER(CONVERT(VARCHAR(36), d.DisputeID)) AS DisputeID
    FROM Application..DSPDisputes d WITH (NOLOCK)
    INNER JOIN Merchant..Merchant m WITH (NOLOCK)
        ON d.LocationID = m.MerchantID
    WHERE d.CreateDate < %s
      AND m.Status = 'D'
      AND m.DeleteDate < %s
    """

    conn = get_db_connection()
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, (CUTOFF_DATE, CUTOFF_DATE))
        rows = cursor.fetchall()
        dispute_ids = [row[0] for row in rows]
    finally:
        conn.close()

    return dispute_ids