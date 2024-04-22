import json
import pymysql
import os


def lambda_handler(event, context):
    # Extract review data from the event
    review = json.loads(event["body"])
    username = review["username"]
    review_content = review["reviewContent"]
    stars = review["stars"]
    date_posted = review[
        "datePosted"
    ]  # Make sure the date is in a format MySQL accepts

    # Connect to MySQL RDS instance using PyMySQL
    connection = pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database="NHTSA_Data",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `userReviews` (`username`, `reviewContent`, `datePosted`, `stars`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, review_content, date_posted, stars))

        connection.commit()
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps("Review saved successfully"),
        }

    except Exception as e:
        print(f"Error: {e}")
        # Error occurred, include CORS headers
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps("Internal Server Error"),
        }

    finally:
        try:
            connection.close()
        except:
            pass
