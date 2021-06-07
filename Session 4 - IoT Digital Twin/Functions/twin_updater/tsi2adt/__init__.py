from typing import List
import logging
import json

import azure.functions as func

from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient


def main(events: List[func.EventHubEvent]):
    for event in events:
        logging.info('Python EventHub trigger processed an event: %s',
                        event.get_body().decode('utf-8'))

        url = "{your ADT endpoint here}"
        credential = DefaultAzureCredential()
        service_client = DigitalTwinsClient(url, credential)

        data = event.get_body()
        j = json.loads(data)

        dtid = j["$dtId"]

        if dtid == "温湿度传感器":
            temperture = j["Temperature"]
            humidity = j["Humidity"]

            logging.info("Room Temp is " + str(temperture))
            logging.info("Room Humidity is " + str(humidity))

            try:
                digita_twin_id = "会议室1801"
                patch = [
                    {
                        "op": "replace",
                        "path": "/Temperature",
                        "value": temperture
                    },
                    {
                        "op": "replace",
                        "path": "/Humidity",
                        "value": humidity
                    }
                ]
                logging.info("Patching Meeting Room Temperature & Humidity Property")
                service_client.update_digital_twin(
                    digita_twin_id,
                    patch
                )

            except HttpResponseError as e:
                logging.error("\nThis twin update has caught an error. {0}".format(e.message))

        elif dtid == "人体感应器":
            occupation = j["IsOccupied"]
            if occupation == 1:
                room_left = 1
                room_status = "Occupied"
            else:
                room_left = 2
                room_status = "Avaliable"
            logging.info ("Room Status is " + room_status)         
            logging.info ("Meeting Room Left in this Level is " + str(room_left))
            try:
                digita_twin_id = "会议室1801"
                patch = [
                    {
                        "op": "replace",
                        "path": "/IsOccupied",
                        "value": occupation
                    }
                ]
                logging.info("Patching Meeting Room Occupation Property")
                service_client.update_digital_twin(
                    digita_twin_id,
                    patch
                )

                digita_twin_id_level = "18层"
                patch_level = [
                    {
                        "op": "replace",
                        "path": "/FreeMeetingRoomCount",
                        "value": room_left
                    }
                ] 
            
                service_client.update_digital_twin(
                    digita_twin_id_level,
                    patch_level
                )
                logging.info("Patching Level Property")

            except HttpResponseError as e:
                logging.error("\nThis twin update has caught an error. {0}".format(e.message))

        else:
            break
