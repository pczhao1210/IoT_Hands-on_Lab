import asyncio
import threading
import datetime
import time
import json
import random
import uuid
from functions import derive_device_key
from six.moves import input
from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import MethodResponse, Message

fw_info = 1.1

# Using this for Connecting through IoT Hub Device Connection String
conn_string = "{Your IoT Hub Connection String Here}"

# Using this for Connecting through Device Provisioning Service (DPS) - "Group Enrollment"
# When provision through "Individual Enrollment", USE SYMMETRIC KEY DIRECTLY
provisioning_host = "global.azure-devices-provisioning.net"
id_scope = "{Your DPS Scope ID Here}"
registration_id = "{Your TO-BE Assigned Device ID Here}"
symmetric_key = "Your Provisioning Master Key Here}"

telemetry_interval = None
send_data = None


async def main():
    
    '''
    # Connect using Device Provisioning Service (DPS)
    device_key = derive_device_key(registration_id,symmetric_key) #Convert from original symmetric key to device key for further enrollment
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=device_key
    )
    registration_result = provisioning_device_client.register()

    print("The status is :", registration_result.status)
    print("The device id is: ", registration_result.registration_state.device_id)
    print("The assigned IoT Hub is: ", registration_result.registration_state.assigned_hub)
    print("The etag is :", registration_result.registration_state.etag)

    if registration_result.status == "assigned":
        print("Provisioning Sucessfully, will send telemetry from the provisioned device")
        device_client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=device_key,
            hostname=registration_result.registration_state.assigned_hub,
            device_id=registration_result.registration_state.device_id,
        )

        device_client.connect()
    '''

    # Connect using Connectiong String
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_string)

    # connect the client
    await device_client.connect()

    # Read Twin Data from Device_Twin, determine if the program should send data to IoT Hub
    data = await device_client.get_twin()
    global telemetry_interval, send_data
    telemetry_interval = data["desired"]["Telemetry_Interval"]
    print("Telemetry Interval is Set to: " + str(telemetry_interval))
    send_data = data["desired"]["Send_Data"]
    if send_data == True:
        print("Send_Data Switch is ON, Start Sending Data...")
    else:
        print("Send_Data Switch is OFF, Please update \"Send_Data\" to \"True\" in device-twin to Start!")


    # define method handlers
    async def method_request_handler(method_request):
        if method_request.name == "Get_FW_info":
            # set response payload
            payload = {"result": True,
                        "data": "The Firmware version now is " + str(fw_info)}
            status = 200  # set return status code
            print(str(datetime.datetime.now()), "Processing Request \"Get_FW_info\" and Report, The Firmware version now is " + str(fw_info))
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            # send response
            await device_client.send_method_response(method_response)
        
        elif method_request.name =="Get_Send_Data_info":
            data = await device_client.get_twin()  # blocking call
            #print(data)
            send_data = data["desired"]["Send_Data"]
            #print(send_data)
            # set response payload
            payload = {"result": send_data,
                        "data": "The Send Data Status is " + str(send_data)}
            status = 200  # set return status code
            print(str(datetime.datetime.now()), "Processing Request \"Get_Send_Data_info\" and Report, The Send_Data Status is " + str(send_data))
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            # send response
            await device_client.send_method_response(method_response)

        elif method_request.name == "FW_Update":
            fw_info_from_method = method_request.payload
            print(str(datetime.datetime.now()), "Received Firmware Upgrade Request: Version " +
                    str(fw_info_from_method)+ ", Initialiazing...")
            time.sleep(2)
            if fw_info >= fw_info_from_method:
                payload = {"result": False,
                        "data": ("The Firmware Version Now is " + str(fw_info) + ", Update Cancelled")}
                status = 403  # set return status code
                print(str(datetime.datetime.now()), "The Firmware Version is Latest, Firmware Upgrade Cancelled")
                method_response = MethodResponse.create_from_method_request(
                    method_request, status, payload
                )
                # send response
                await device_client.send_method_response(method_response)
            if fw_info < fw_info_from_method:
                payload = {"result": True,
                    "data": ("The Firmware Version Now is " + str(fw_info)+ ", Update Task Now Begin...")}
                status = 200  # set return status code
                method_response = MethodResponse.create_from_method_request(
                    method_request, status, payload
                )
                # send response
                await device_client.send_method_response(method_response)
                print(str(datetime.datetime.now()), "Step 1: New Firmware Version " + str(fw_info_from_method),
                        "is Set, Firmware Downloading...")
                time.sleep(2)
                print(str(datetime.datetime.now()), "Step 2: Downloading Success, Validation Firmware file...")
                time.sleep(2)
                print(str(datetime.datetime.now()), "Step 3: Firmware Validation Passed, Start Firmware Upgrading...")
                time.sleep(2)
                print(str(datetime.datetime.now()), "Step 4: Upgrading Sucessful, Rebooting Device...")
                time.sleep(2)
                print(str(datetime.datetime.now()), "Step 5: Device Successful Reconnected !!!")
        
        else:
            # set response payload
            payload = {"result": False, "data": "Unrecognized Method"}
            status = 400  # set return status code
            print(str(datetime.datetime.now()), "Receiving Unknown Method: " + method_request.name)
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            # send response
            await device_client.send_method_response(method_response)

    # define behavior for receiving a message
    async def message_receive_handler(message):
        print(str(datetime.datetime.now()), "Received Message:")
        print(message.data.decode())
        if len(message.custom_properties) > 0:
            print("With Custom Properties:")
            print(message.custom_properties)

    # Twin Listener
    async def twin_patch_handler(data):
        global telemetry_interval, send_data
        #data = patch  # blocking call
        if "Telemetry_Interval" in data:
            telemetry_interval = data["Telemetry_Interval"]
            print(str(datetime.datetime.now()), "Telemetry Interval has set to", telemetry_interval)
        if "Send_Data" in data:
            send_data = data["Send_Data"]
            if send_data == True:
                print(str(datetime.datetime.now()), "Send Data has set to " + str(send_data) +
                    ", Continue Sending Data...")
            else:
                print(str(datetime.datetime.now()), "Send Data has set to " + str(send_data) +
                    ", Please update \"Send_Data\" to \"True\" in device-twin to restart!")
        reported_properties = {
            "Telemetry_Interval": telemetry_interval,
            "Send_Data": send_data
        }
        await device_client.patch_twin_reported_properties(reported_properties)
   
    # define send message to iot hub
    async def send_telemetry(device_client):
        global send_data, telemetry_interval
        telemetry_data_raw = '{{"Voltage": {voltage},"Ampere": {ampere},"Walt": {walt}}}'
        while True:
            if send_data == True:
                voltageset = 220 + (random.random() * 10)
                ampereset = 10 + random.random()
                waltset = (voltageset * ampereset) / 1000
                telemetry_data_formatted = telemetry_data_raw.format(
                    voltage=voltageset, ampere=ampereset, walt=waltset)
                telemetry_data = Message(telemetry_data_formatted)
                print(str(datetime.datetime.now()),
                        "Sending Telemetry: ", telemetry_data)
                if waltset > 2.496:  # 229*10.9 = 2.496
                    telemetry_data.custom_properties["Alert"] = "Almost_Full_Capacity"
                    telemetry_data.message_id = uuid.uuid4()
                await device_client.send_message(telemetry_data)
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
    device_client.on_method_request_received = method_request_handler
    device_client.on_message_received = message_receive_handler
    device_client.on_twin_desired_properties_patch_received = twin_patch_handler
    
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


    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()

