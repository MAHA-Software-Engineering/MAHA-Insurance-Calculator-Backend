import requests
import boto3
import json
from dotenv import load_dotenv
import os

load_dotenv()
# Initialize S3 client
s3 = boto3.client('s3')
s3_bucket = os.environ['s3_bucket']

def fetch_data(endpoint):
    """Fetch data from a given endpoint."""
    response = requests.get(endpoint)
    return response.json() if response.status_code == 200 else None

def fetch_ratings_data(years, vehicles):
    """Fetch safety ratings data for specified vehicles and years."""
    base_url = "https://api.nhtsa.gov/SafetyRatings"
    fetched_data = []
    for year in years:
        for vehicle in vehicles:
            variants_endpoint = f"{base_url}/modelyear/{year}/make/{vehicle['make']}/model/{vehicle['model']}"
            variants_data = fetch_data(variants_endpoint)
            if variants_data and 'Results' in variants_data:
                for variant in variants_data['Results']:
                    vehicle_id = variant['VehicleId']
                    rating_endpoint = f"{base_url}/VehicleId/{vehicle_id}"
                    rating_data = fetch_data(rating_endpoint)
                    if rating_data:
                        fetched_data.extend(rating_data['Results'])
    return fetched_data

def fetch_recall_data(years, vehicles):
    """Fetch recall data for specified vehicles and years."""
    base_url = "https://api.nhtsa.gov/recalls/recallsByVehicle"
    fetched_data = []
    for year in years:
        for vehicle in vehicles:
            recall_endpoint = f"{base_url}?make={vehicle['make']}&model={vehicle['model']}&modelYear={year}"
            recall_data = fetch_data(recall_endpoint)
            if recall_data and 'results' in recall_data:
                fetched_data.extend(recall_data['results'])
    return fetched_data

def lambda_handler(event, context):
    years = range(2017, 2023)
    vehicles = [{'make': 'Toyota', 'model': 'Camry'}, 
                {'make': 'Honda', 'model': 'Civic'}, 
                {'make': 'Ford', 'model': 'F-150'}, 
                {'make': 'Audi', 'model': 'A6'}, 
                {'make': 'BMW', 'model': 'X5'},
                {'make': 'Toyota', 'model': 'Corolla'},
                {'make': 'Toyota', 'model': 'RAV4'},
                {'make': 'Honda', 'model': 'Accord'},
                {'make': 'Honda', 'model': 'Pilot'},
                {'make': 'Ford', 'model': 'Mustang'},
                {'make': 'Audi', 'model': 'RS5'},
                {'make': 'BMW', 'model': 'X3'},]

    # Fetch, filter, and upload safety ratings data
    ratings_data = fetch_ratings_data(years, vehicles)
    relevant_fields_ratings = ['OverallRating', 'OverallFrontCrashRating', 'OverallSideCrashRating', 'RolloverRating', 'NHTSAElectronicStabilityControl', 'NHTSAForwardCollisionWarning', 'NHTSALaneDepartureWarning', 'ComplaintsCount', 'RecallsCount', 'InvestigationCount', 'ModelYear', 'Make', 'Model', 'VehicleDescription', 'VehicleId']
    filtered_ratings_data = [{field: item.get(field) for field in relevant_fields_ratings} for item in ratings_data]
    s3.put_object(Bucket=s3_bucket, Key='rating_info.json', Body=json.dumps(filtered_ratings_data, indent=4))
    
    # Fetch, filter, and upload recall data
    recall_data = fetch_recall_data(years, vehicles)
    relevant_fields_recall = ['Manufacturer', 'NHTSACampaignNumber', 'Component', 'Summary', 'Consequence', 'Remedy', 'ModelYear', 'Make', 'Model']
    filtered_recall_data = [{field: item.get(field) for field in relevant_fields_recall} for item in recall_data]
    s3.put_object(Bucket=s3_bucket, Key='recall_info.json', Body=json.dumps(filtered_recall_data, indent=4))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Data successfully uploaded to S3')
    }
