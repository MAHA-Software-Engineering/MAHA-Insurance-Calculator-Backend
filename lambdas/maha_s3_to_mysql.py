import json
import boto3
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
def lambda_handler(event, context):
    # Establish database connection
    db_connection = pymysql.connect(
        host= os.environ['host'],
        user= os.environ['user'],
        password= os.environ['password'],
        db= os.environ['db'],
        port=3306
    )
    
    # Create an S3 client
    s3_client = boto3.client('s3')
    
    # Get bucket and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Get the object from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    data = json.loads(response['Body'].read().decode('utf-8'))
    
    with db_connection.cursor() as cursor:
        # Create tables if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recall_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Manufacturer VARCHAR(255),
                NHTSACampaignNumber INT,
                Component VARCHAR(300),
                Summary TEXT,
                Consequence TEXT,
                Remedy TEXT,
                ModelYear INT,
                Make VARCHAR(15),
                Model VARCHAR(20)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rating_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                OverallRating VARCHAR(50),
                OverallFrontCrashRating VARCHAR(50),
                OverallSideCrashRating VARCHAR(50),
                RolloverRating VARCHAR(50),
                NHTSAElectronicStabilityControl VARCHAR(50),
                NHTSAForwardCollisionWarning VARCHAR(50),
                NHTSALaneDepartureWarning VARCHAR(50),
                ComplaintsCount INT,
                RecallsCount INT,
                InvestigationCount INT,
                ModelYear INT,
                Make VARCHAR(255),
                Model VARCHAR(255),
                VehicleDescription TEXT,
                VehicleId INT
            );
        """)
        
        # Determine if data is for recall or rating
        if 'recall_info' in object_key:
            for item in data:
                sql = """INSERT INTO recall_info (Manufacturer, NHTSACampaignNumber, Component, Summary, Consequence, Remedy, ModelYear, Make, Model)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                values = (
                    item['Manufacturer'],
                    item['NHTSACampaignNumber'],
                    item['Component'],
                    item['Summary'],
                    item['Consequence'],
                    item['Remedy'],
                    item['ModelYear'],
                    item['Make'],
                    item['Model']
                )
                cursor.execute(sql, values)
        elif 'rating_info' in object_key:
            for item in data:
                sql = """INSERT INTO rating_info (OverallRating, OverallFrontCrashRating, OverallSideCrashRating, RolloverRating,
                          NHTSAElectronicStabilityControl, NHTSAForwardCollisionWarning, NHTSALaneDepartureWarning, ComplaintsCount,
                          RecallsCount, InvestigationCount, ModelYear, Make, Model, VehicleDescription, VehicleId)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                values = (
                    item.get('OverallRating'),
                    item.get('OverallFrontCrashRating'),
                    item.get('OverallSideCrashRating'),
                    item.get('RolloverRating'),
                    item.get('NHTSAElectronicStabilityControl'),
                    item.get('NHTSAForwardCollisionWarning'),
                    item.get('NHTSALaneDepartureWarning'),
                    item.get('ComplaintsCount', 0),  # Defaulting to 0 if not present
                    item.get('RecallsCount', 0),  # Defaulting to 0 if not present
                    item.get('InvestigationCount', 0),  # Defaulting to 0 if not present
                    item['ModelYear'],
                    item['Make'],
                    item['Model'],
                    item.get('VehicleDescription', ''),  # Defaulting to empty string if not present
                    item['VehicleId']
                )
                cursor.execute(sql, values)
        
        # Commit changes
        db_connection.commit()
    
    # Close connection
    db_connection.close()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data processed successfully')
    }
