import pymysql
import json
# delete this for the actual lambda
from dotenv import load_dotenv
import os
# 
def lambda_handler(event, context):
    # Database connection details
    db_connection = pymysql.connect(
        host = os.environ['host'],
        user = os.environ['user'],
        password = os.environ['password'],
        db = os.environ['db'],
        port=3306
    )

    cursor = db_connection.cursor()

    # SQL query to fetch specific columns
    query = "SELECT Component, Summary, Consequence, Remedy FROM recall_info" 
    cursor.execute(query)

    # Fetch the results
    rows = cursor.fetchall()

    # Prepare the data for JSON output
    result = []
    for row in rows:
        result.append({
            "Component": row[0],
            "Summary": row[1],
            "Consequence": row[2],
            "Remedy": row[3]
        })

    # Close the connection
    cursor.close()
    db_connection.close()

    # Return the query results
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
