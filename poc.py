import argparse
import asyncio
from datetime import datetime
import os
import requests
import websockets
import json
import sqlite3
import logging
from datetime import timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

parser = argparse.ArgumentParser(description='Shelly Plug POC')
parser.add_argument('--email', '-e', help='Shelly email',
                    required=True)
parser.add_argument('--password', '-p', help='Shelly password',
                    required=True)
parser.add_argument('--server', '-s', help='Shelly server',
                    default='shelly-62-eu.shelly.cloud')
parser.add_argument('--database', '-d', help='SQLite database',
                    default='shelly_plug.db')
args = parser.parse_args()

EMAIL: str = args.email
PASSWORD_SHA1: str = args.password
SERVER: str = args.server
SQLITE_DATABASE: str = args.database


def _get_authorization_code():
    """
    Get authorization code for OAuth2.

    This mimics the request done by the official OAuth login webpage.
    """
    res = requests.post(
        "https://api.shelly.cloud/oauth/login",
        data={
            "email": EMAIL,
            "password": PASSWORD_SHA1,
            "response_type": "",
            "client_id": "shelly-diy",
        },
    )

    # TODO: add error management
    return res.json()["data"]["code"]


def get_access_token() -> str:
    """Login on the API."""
    res = requests.post(
        f"https://{SERVER}/oauth/auth",
        data={
            "client_id": "shelly-diy",
            "grant_type": "code",
            "code": _get_authorization_code(),
        },
    )

    # TODO: add error management
    return res.json().get("access_token")


async def main():
    logging.info("Opening local database...")
    database_connection = sqlite3.connect(SQLITE_DATABASE)
    database_cursor = database_connection.cursor()

    logging.info("Login...")


    # Create table
    database_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
            date datetimetz  NOT NULL,
            content jsonb  NOT NULL
        )
        """
    )
    database_connection.commit()

    logging.info("Connecting to websocket")
    access_token = get_access_token()
    async for websocket in websockets.connect(f"wss://{SERVER}:6113/shelly/wss/hk_sock?t={access_token}"):
        logging.info("Connected")
        try:
            async for message in websocket:
                now = datetime.now(timezone.utc)
                parsed_message = json.loads(message)
                logging.info("Processing message received at %s: %s", now, json.dumps(parsed_message, indent=2))

                if 'status' in parsed_message and 'serial' in parsed_message['status']:
                    event_time = datetime.fromtimestamp(
                        parsed_message["status"]["serial"], timezone.utc)
                    if event_time < now:
                        logging.info("Event time: %s (%s ago)", event_time, now-event_time)

                # Insert in database
                database_cursor.execute(
                    "INSERT INTO logs( date, content ) VALUES( ?, ? )",
                    (now, message,),
                )
                database_connection.commit()

        except websockets.ConnectionClosed as err:
            logging.warning(f"Error on websocket: {err}, reconnecting...")
            access_token = get_access_token()


if __name__ == "__main__":
    asyncio.run(main())
