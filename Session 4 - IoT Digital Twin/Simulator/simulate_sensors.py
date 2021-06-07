import asyncio
import threading
import datetime
import time
import json
import random
import uuid
from functions import derive_device_key
from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import MethodResponse, Message

telemetry_interval = 10

# Using this for Connecting through IoT Hub Device Connection String
conn_string = "HostName=iot-hub-general.azure-devices.net;DeviceId=ADT-Sensor;SharedAccessKey=2Zno4Y3dmJg2bhaFGNb3HUy83Ate2ZX6rdvyFmKDyEI="

async def main():

    # Connect using Connectiong String
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_string)

    # connect the client
    await device_client.connect()

    # define send message to iot hub
    async def send_telemetry(device_client):
        # Form the sturcture of message payload
        telemetry_data_raw_temp = '{{"Device_Type": "Temp_Sensor", "Temperature": {temperature},"Humidity": {humidity}}}'
        telemetry_data_raw_human = '{{"Device_Type": "Human_Sensor", "IsOccupied": {occupation_status}}}'
        # Generate payload data
        while True:
            temperature_set = 22 + random.random()*3
            humidity_set = 50 + random.random()*10
            if humidity_set >= 55:
                occupation_set = 1
            else:
                occupation_set = 0

            # Form messages sent to IoT Hub
            temp_data_formatted = telemetry_data_raw_temp.format(temperature=temperature_set, humidity=humidity_set, occupation_status=occupation_set)
            human_data_formatted = telemetry_data_raw_human.format(occupation_status=occupation_set)
            telemetry_data_temp = Message(temp_data_formatted)
            telemetry_data_human = Message(human_data_formatted)

            # Sending data to IoT Hub with interval
            
            await device_client.send_message(telemetry_data_temp)
            print(str(datetime.datetime.now()), "Sending Telemetry: ", telemetry_data_temp)
            await asyncio.sleep(5) 
            await device_client.send_message(telemetry_data_human)
            print(str(datetime.datetime.now()), "Sending Telemetry: ", telemetry_data_human)
            await asyncio.sleep(telemetry_interval)

    def send_telemetry_sync(device_client):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(send_telemetry(device_client))

    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    # Set handlers to the client   
    send_telemetry_Thread = threading.Thread(target=send_telemetry_sync, args=(device_client,))
    send_telemetry_Thread.daemon = True
    send_telemetry_Thread.start()

    # Run the stdin listener in the event loop
    loop = asyncio.get_event_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for method calls
    await user_finished

    # Finally, disconnect
    await device_client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
