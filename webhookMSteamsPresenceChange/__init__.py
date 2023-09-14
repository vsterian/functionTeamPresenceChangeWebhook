import logging
import azure.functions as func
import requests
import json

# Define the WebCoRE piston URI
webcore_piston_uri = "https://cloud.hubitat.com/api/b29ea9c3-1f17-4fdd-aeb0-e3ad2b8d0daa/apps/42/execute/:db1450619452db181809fba970e073bc:?access_token=20ebb836-563c-46f3-b7fd-ed5a8e46296e"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Check if this is a validation request
    validation_token = req.params.get("validationToken")
    if validation_token:
        # Return the validation token as plain text
        return func.HttpResponse(validation_token, mimetype="text/plain")

    try:
        # Parse the incoming JSON body
        data = req.get_json()

        # Log the entire JSON response body
        logging.info("Received JSON body:")
        logging.info(json.dumps(data, indent=4))

        # Extract the presence change data
        presence_data = data["value"][0]["resourceData"]

        # Extract the "activity" and "availability" values
        activity = presence_data.get("activity")
        availability = presence_data.get("availability")

        # Log the extracted values
        logging.info(f"Activity: {activity}")
        logging.info(f"Availability: {availability}")

        # Prepare the data to send to the WebCoRE piston
        webcore_data = {
            "activity": activity,
            "availability": availability
        }

        # Send the data to the WebCoRE piston as JSON
        response = requests.post(webcore_piston_uri, json=webcore_data)

        # Check the response status code and log the result
        if response.status_code == 200:
            logging.info("Data sent to WebCoRE piston successfully.")
        else:
            logging.error(f"Failed to send data to WebCoRE piston. Status code: {response.status_code}")

        # Return a 202 Accepted response to acknowledge receipt of the notification
        return func.HttpResponse(status_code=202)

    except Exception as e:
        # Log any errors and return a 400 Bad Request response
        logging.error(f"Error processing the request: {str(e)}")
        return func.HttpResponse("Bad Request", status_code=400)
