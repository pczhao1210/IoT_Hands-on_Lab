import asyncio
import threading
import datetime
import time
import json
import random
import uuid
from functions import derive_device_key
from six.moves import input
from azure.iot.device import MethodResponse, Message, IoTHubDeviceClient, ProvisioningDeviceClient

fw_info = 1.1

# Connect using Device Provisioning Service (DPS) - Group Enrollment
# When provision through Individual Enrollment, USE SYMMETRIC KEY DIRECTLY
provisioning_host = "global.azure-devices-provisioning.cn"
id_scope = "{Your DPS Scope ID Here}"
registration_id = "{Your TO-BE Assigned Device ID Here}"
symmetric_key = "{Your Provisioning Master Key Here}"

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

data = device_client.get_twin()
telemetry_interval = data["desired"]["Telemetry_Interval"]
print("Telemetry Interval is Set to: " + str(telemetry_interval))
send_data = data["desired"]["Send_Data"]
if send_data == True:
    print("Send_Data Switch is ON, Start Sending Data...")
else:
    print("Send_Data Switch is OFF, Please update \"Send_Data\" to \"True\" in device-twin to Start!")

# connect the client.
device_client.connect()

# define method listeners
def Get_FW_info_listener(device_client):
    while True:
        # Wait for method calls
        method_request = device_client.receive_method_request("Get_FW_info")
        # set response payload
        payload = {"result": True,
                    "data": "The Firmware version now is " + str(fw_info)}
        status = 200  # set return status code
        print(str(datetime.datetime.now()), "Processing Request \"Get_FW_info\" and Report, The Firmware version now is " + str(fw_info))
        method_response = MethodResponse.create_from_method_request(
            method_request, status, payload
        )
        # send response
        device_client.send_method_response(method_response)

def Get_Send_Data_info_listener(device_client):
    while True:
        # Wait for method calls
        method_request = device_client.receive_method_request("Get_Send_Data_info")
        data = device_client.get_twin()  # blocking call
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
        device_client.send_method_response(method_response)

def FW_updater_listener(device_client):
    while True:
        method_request = device_client.receive_method_request("FW_Update")
        fw_info_from_method = method_request.payload
        print(str(datetime.datetime.now()), "Received Firmware Upgrade Request: Version" +
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
            device_client.send_method_response(method_response)
        if fw_info < fw_info_from_method:
            payload = {"result": True,
                "data": ("The Firmware Version Now is " + str(fw_info)+ ", Update Task Now Begin...")}
            status = 200  # set return status code
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )
            # send response
            device_client.send_method_response(method_response)
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

def generic_method_listener(device_client):
    while True:
        method_request = (
            device_client.receive_method_request()
        )  # Wait for unknown method calls
        # set response payload
        payload = {"result": False, "data": "Unrecognized Method"}
        status = 400  # set return status code
        print(str(datetime.datetime.now()), "Receiving Unknown Method: " + method_request.name)
        method_response = MethodResponse.create_from_method_request(
            method_request, status, payload
        )
        # send response
        device_client.send_method_response(method_response)

# define behavior for receiving a message
def message_listener(device_client):
    while True:
        message = device_client.receive_message()  # blocking call
        print(str(datetime.datetime.now()), "Received Message:")
        print(message.data.decode())
        if len(message.custom_properties) > 0:
            print(str(datetime.datetime.now()), "With Custom Properties:")
            print(message.custom_properties)

# define send message to iot hub
def send_telemetry(device_client):
    global telemetry_interval, send_data
    telemetry_data_raw = '{{"Voltage": {voltage},"Ampere": {ampere},"Walt": {walt}}}'
    while True:
        time.sleep(telemetry_interval)
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
            device_client.send_message(telemetry_data)
           

# Twin Listener
def twin_patch_listener(device_client):
    global telemetry_interval, send_data
    while True:
        try:
            data = device_client.receive_twin_desired_properties_patch()  # blocking call
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
            device_client.patch_twin_reported_properties(reported_properties)

        except KeyboardInterrupt:
            print("Exited")


# Schedule tasks for Listener
Get_FW_info_listener_Thread = threading.Thread(target=Get_FW_info_listener, args=(device_client,))
Get_FW_info_listener_Thread.daemon = True
Get_FW_info_listener_Thread.start()

Get_Send_Data_info_listener_Thread = threading.Thread(target=Get_Send_Data_info_listener, args=(device_client,))
Get_Send_Data_info_listener_Thread.daemon = True
Get_Send_Data_info_listener_Thread.start()

FW_updater_listener_Thread = threading.Thread(target=FW_updater_listener, args=(device_client,))
FW_updater_listener_Thread.daemon = True
FW_updater_listener_Thread.start()

generic_method_listener_Thread = threading.Thread(target=generic_method_listener, args=(device_client,))
generic_method_listener_Thread.daemon = True
generic_method_listener_Thread.start()

message_listener_Thread = threading.Thread(target=message_listener, args=(device_client,))
message_listener_Thread.daemon = True
message_listener_Thread.start()

twin_patch_listener_Thread = threading.Thread(target=twin_patch_listener, args=(device_client,))
twin_patch_listener_Thread.daemon = True
twin_patch_listener_Thread.start()

send_telemetry_Thread = threading.Thread(target=send_telemetry, args=(device_client,))
send_telemetry_Thread.daemon = True
send_telemetry_Thread.start()

# Wait for user to indicate they are done listening for messages
while True:
    try:
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break
    except KeyboardInterrupt:
        print("Quitting...")
        break

# Finally, disconnect
device_client.disconnect()


