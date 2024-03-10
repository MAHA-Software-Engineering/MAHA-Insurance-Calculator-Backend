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

    # Extract parameters from the event
    params = event.get('queryStringParameters', {})
    year = params.get('year', None)
    make = params.get('make', None)
    model = params.get('model', None)

    # Initialize the result dictionary
    result = {
        'ratings': [],
        'recalls': []
    }

    # SQL query for rating information
    rating_conditions = []
    if year:
        rating_conditions.append(f"ModelYear = '{year}'")
    if make:
        rating_conditions.append(f"Make = '{make}'")
    if model:
        rating_conditions.append(f"Model = '{model}'")
    
    rating_condition_str = " AND ".join(rating_conditions) if rating_conditions else "1=1"
    
    rating_query = f"SELECT VehicleDescription, OverallRating, OverallFrontCrashRating, OverallSideCrashRating, RolloverRating, NHTSAElectronicStabilityControl, NHTSAForwardCollisionWarning, NHTSALaneDepartureWarning, ComplaintsCount, RecallsCount, InvestigationCount FROM rating_info WHERE {rating_condition_str}"
    cursor.execute(rating_query)

    rating_rows = cursor.fetchall()
    for row in rating_rows:
        result['ratings'].append({
            "VehicleDescription": row[0],
            "OverallRating": row[1],
            "OverallFrontCrashRating": row[2],
            "OverallSideCrashRating": row[3],
            "RolloverRating": row[4],
            "NHTSAElectronicStabilityControl": row[5],
            "NHTSAForwardCollisionWarning": row[6],
            "NHTSALaneDepartureWarning": row[7],
            "ComplaintsCount": row[8],
            "RecallsCount": row[9],
            "InvestigationCount": row[10]
        })

    # SQL query for recall information
    recall_conditions = rating_conditions  # Assuming the conditions are the same for both queries
    recall_condition_str = rating_condition_str  # Reusing the condition string
    
    recall_query = f"SELECT Component, Summary, Consequence, Remedy FROM recall_info WHERE {recall_condition_str}"
    cursor.execute(recall_query)

    recall_rows = cursor.fetchall()
    for row in recall_rows:
        result['recalls'].append({
            "Component": row[0],
            "Summary": row[1],
            "Consequence": row[2],
            "Remedy": row[3]
        })

    # Closing the cursor and database connection
    cursor.close()
    db_connection.close()

    # Check if no information found
    if not rating_rows and not recall_rows:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,OPTIONS',
            },
            'body': json.dumps({"message": "No information on this vehicle"})
        }

    # Return combined query results with CORS headers
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
        },
        'body': json.dumps(result)
    }
