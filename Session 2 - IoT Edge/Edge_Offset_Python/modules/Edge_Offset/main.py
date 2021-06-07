# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
import json
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient

# global counters
TEMPERATURE_THRESHOLD = 25
TWIN_CALLBACKS = 0
RECEIVED_MESSAGES = 0
ENCODED_OFFSET = 0
ENCODED_SWITCH = True

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # define behavior for receiving an input message on input1
        async def input1_listener(module_client):
            global RECEIVED_MESSAGES
            global TEMPERATURE_THRESHOLD
            global ENCODED_OFFSET
            global ENCODED_SWITCH
            while True:
                try:
                    #消息中machine温度大于设定值TEMPERATURE_THRESHOLD, 为消息添加Alert属性，输出到output1通路
                    input_message = await module_client.receive_message_on_input("input1")  # blocking call
                    message = input_message.data
                    size = len(message)
                    message_text = message.decode('utf-8')
                    print ( "    Data: <<<%s>>> & Size=%d" % (message_text, size) )
                    custom_properties = input_message.custom_properties
                    print ( "    Properties: %s" % custom_properties )
                    RECEIVED_MESSAGES += 1
                    print ( "    Total messages received: %d" % RECEIVED_MESSAGES )
                    data = json.loads(message_text)
                    if "machine" in data and "temperature" in data["machine"] and data["machine"]["temperature"] > TEMPERATURE_THRESHOLD:
                        custom_properties["MessageType"] = "Alert"
                        print ( "Machine temperature %s exceeds threshold %s" % (data["machine"]["temperature"], TEMPERATURE_THRESHOLD))
                        await module_client.send_message_to_output(input_message, "output1")
                    
                    #为所有的温度设置偏移量ENCODED_OFFSET，输出到output2通路
                    if ENCODED_SWITCH == True:
                        machine_pres = data["machine"]["pressure"]
                        ambient_humi = data["ambient"]["humidity"]
                        encoded_machine_temp = data["machine"]["temperature"] + ENCODED_OFFSET
                        encoded_ambient_temp = data["ambient"]["temperature"] + ENCODED_OFFSET
                        c_time =  data["timeCreated"]
                        encoded_data = {
                                            "ENCODED": ENCODED_SWITCH,
                                            "machine": {
                                                "temperature": encoded_machine_temp,
                                                "pressure": machine_pres
                                            },
                                            "ambient": {
                                                "temperature": encoded_ambient_temp,
                                                "humidity": ambient_humi
                                            },
                                            "timeCreated": c_time
                                        }
                        await module_client.send_message_to_output(json.dumps(encoded_data),"output2")
                    else:
                        print("Ecodedswitch is OFF, please set it to 'ture' in module twin to start ENCODE!")
                    
                except Exception as ex:
                    print ( "Unexpected error in input1_listener: %s" % ex )

        # twin_patch_listener is invoked when the module twin's desired properties are updated.
        async def twin_patch_listener(module_client):
            global TWIN_CALLBACKS
            global TEMPERATURE_THRESHOLD
            global ENCODED_OFFSET
            global ENCODED_SWITCH
            while True:
                try:
                    data = await module_client.receive_twin_desired_properties_patch()  # blocking call
                    print( "The data in the desired properties patch was: %s" % data)
                    if "TemperatureThreshold" in data:
                        TEMPERATURE_THRESHOLD = data["TemperatureThreshold"]
                        print ("TemperatureThreshold has set to", TEMPERATURE_THRESHOLD)
                    if "EncodedOffset" in data:
                        ENCODED_OFFSET = data["EncodedOffset"]
                        print ("EncodedOffset has set to", ENCODED_OFFSET)
                    if "EncodedSwitch" in data:
                        ENCODED_SWITCH = data["EncodedSwitch"]
                        print ("EncodedSwitch has set to", ENCODED_SWITCH)                    
                    TWIN_CALLBACKS += 1
                    print ( "Total calls confirmed: %d\n" % TWIN_CALLBACKS )
                    patch = {
                        "TemperatureThreshold":TEMPERATURE_THRESHOLD, 
                        "EncodedOffset":ENCODED_OFFSET,
                        "EncodedSwitch":ENCODED_SWITCH}
                    await module_client.patch_twin_reported_properties(patch)
                except Exception as ex:
                    print ( "Unexpected error in twin_patch_listener: %s" % ex )

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        # Schedule task for C2D Listener
        listeners = asyncio.gather(input1_listener(module_client), twin_patch_listener(module_client))

        print ( "The sample is now waiting for messages. ")

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())