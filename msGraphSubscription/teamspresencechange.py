import requests
import json
import os
import threading
import logging  # Import the logging module
from azure.identity import InteractiveBrowserCredential
from datetime import datetime, timedelta

# Azure AD App credentials
client_id = '09be529a-eedd-46f5-8af4-be2d7332c552'
tenant_id = '72f988bf-86f1-41af-91ab-2d7cd011db47'

# MS Teams user id
user_id = '6e65cc58-12fb-4c0d-befa-147fe89270c9'

# Create an instance of InteractiveBrowserCredential
credential = InteractiveBrowserCredential(client_id=client_id, tenant_id=tenant_id, redirect_uri='http://localhost:8000')



# Configure logging
logging.basicConfig(level=logging.INFO)

def renew_subscription():
    # Get a token for the Graph API scope
    token = credential.get_token('Presence.Read.All')
    expiration_time = datetime.utcnow() + timedelta(minutes=9)
    expiration_time_str = expiration_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    if token:
        # Call a protected API with the access token.
        headers = {'Authorization': 'Bearer ' + token.token}

        # Create a subscription to presence changes
        subscription_data = {
            "changeType": "updated",
            "notificationUrl": "https://wildteamspresence1.azurewebsites.net/api/webhookMSteamsPresenceChange?code=B6v6velmdkfZteTEe2R50tMbiexjlfYG7FRFH9wQuFPSAzFuA9NPgQ==",
            "resource": f"/communications/presences/{user_id}",
            "expirationDateTime": expiration_time_str,
        }

        response = requests.post(
            'https://graph.microsoft.com/beta/subscriptions',
            headers=headers,
            json=subscription_data
        )

        # Log the JSON response
        logging.info(f"Response JSON: {response.text}")

        if response.status_code == 201:
            print("Subscription renewed successfully.")
        elif response.status_code == 409:    #####This does not work so far
            # Extract and print the subscriptionId from the response
            print("response when409:",json.loads(response.text) )
            existing_subscription_id = None
            try:
                response_json = json.loads(response.text)
                if 'id' in response_json:
                    existing_subscription_id = response_json['id']
            except (KeyError, ValueError, TypeError):
                pass
            print(f"A subscription already exists with subscriptionId: {existing_subscription_id}")
        else:
            print(f"Failed to renew subscription. Status code: {response.status_code}. Message: {response.text}")
    else:
        print("Failed to acquire token.")

    # Schedule the next renewal
    threading.Timer(600, renew_subscription).start()

# Start the first renewal
renew_subscription()
