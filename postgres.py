import psycopg2
import json
from datetime import datetime


class Postgres:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    # creates a record in PostgreSQL events table
    # name (varchar), description (varchar), meta (json), result (json), created_at (timestamp)
    def create_record(self, meta, output_video):
        try:
            connection = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
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
