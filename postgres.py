import psycopg2
import os
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


# creates a record in PostgreSQL events table
# name (varchar), description (varchar), meta (json), result (json), created_at (timestamp)
def create_record(meta, output_video):
    try:
        connection = psycopg2.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO events VALUES ('Video concatenation', '', '{json.dumps(meta)}',
                '{json.dumps({"link": f"https://ffmpeg-video-examples.s3.amazonaws.com/{output_video}"})}',
                '{datetime.now()}');"""
            )
    except Exception as e:
        print("An error while working with PostgreSQL: ", e)
    finally:
        if connection:
            connection.close()
