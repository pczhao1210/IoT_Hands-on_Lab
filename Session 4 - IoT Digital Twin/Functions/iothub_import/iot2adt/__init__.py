from typing import List
import logging
import json

import azure.functions as func

from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient


def main(events: List[func.EventHubEvent]):
    for event in events:
        logging.info('Python EventHub trigger processed an event: %s', event.get_body().decode('utf-8'))

        url = "{Your ADT Endpoint Here}"
        credential = DefaultAzureCredential()
        service_client = DigitalTwinsClient(url, credential)

        data = event.get_body()
        j = json.loads(data)

        if j["Device_Type"] == "Temp_Sensor":        
            temperature = round(j["Temperature"],2)
            humidity = round(j["Humidity"],2)

            logging.info("The Temperature in Room is " + str(temperature))
            logging.info("The Humidity in Room is " + str(humidity))

            try:
                digita_twin_id = "温湿度传感器"
                #telemetry_payload = {"Temperature": temperature, "Humidity": humidity}
                patch = [
                    {
                        "op": "replace",
                        "path": "/Temperature",
                        "value": temperature
                    },
                    {
                        "op": "replace",
                        "path": "/Humidity",
                        "value": humidity
                    }
                ] 
                #service_client.publish_telemetry(
                #    digita_twin_id,
                #    telemetry_payload
                #)
                #logging.info("Sending Temperature Telemetry")
                service_client.update_digital_twin(
                    digita_twin_id,
                    patch
                )
                logging.info("Patching Temp Property")

            except HttpResponseError as e:
                logging.error("\nThis twin update has caught an error. {0}".format(e.message))
        
        else:
            occupation = j["IsOccupied"]
            logging.info("The Occupation Status in Room is " + str(occupation))

            try:
                # Publish telemetry message
                digita_twin_id = "人体感应器"
                #telemetry_payload = {"IsOccupied": occupation}
                patch = [
                    {
                        "op": "replace",
                        "path": "/IsOccupied",
                        "value": occupation
                    }
                ] 
                #service_client.publish_telemetry(
                #    digita_twin_id,
                #    telemetry_payload
                #)
                #logging.info("Sending Occupation Telemetry")
                service_client.update_digital_twin(
                    digita_twin_id,
                    patch
                )
                logging.info("Patching Occupation Property")

            except HttpResponseError as e:
                logging.error("\nThis twin update has caught an error. {0}".format(e.message))
