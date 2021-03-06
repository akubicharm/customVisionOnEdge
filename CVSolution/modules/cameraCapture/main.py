import time
import sys
import os
import requests
import json

import iothub_client
# pylint: disable=E0611
from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

from pathlib import Path

# pylint: disable=E0401

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
MESSAGE_TIMEOUT = 10000

# Choose HTTP, AMQP or MQTT as transport protocol.
PROTOCOL = IoTHubTransportProvider.MQTT

# global counters
SEND_CALLBACKS = 0

# Send a message to IoT Hub
# Route output1 to $upstream in deployment.template.json


def send_to_hub(strMessage):
    message = IoTHubMessage(bytearray(strMessage, 'utf8'))
    hubManager.send_event_to_output("output1", message, 0)

# Callback received when the message that we send to IoT Hub is processed.


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    SEND_CALLBACKS += 1
    print("Confirmation received for message with result = %s" % result)
    print("   Total calls confirmed: %d \n" % SEND_CALLBACKS)

# Send an image to the image classifying server
# Return the JSON response from the server with the prediction result


def sendFrameForProcessing(imagePath, imageProcessingEndpoint):
    headers = {'Content-Type': 'application/octet-stream'}

    with open(imagePath, mode="rb") as test_image:
        try:
            response = requests.post(
                imageProcessingEndpoint, headers=headers, data=test_image)
            print("Response from classification service: (" +
                  str(response.status_code) + ") " + json.dumps(response.json()) + "\n")
        except Exception as e:
            print(e)
            print("Response from classification service: (" +
                  str(response.status_code))

    return json.dumps(response.json())


class HubManager(object):
    def __init__(self, protocol, message_timeout):
        self.client_protocol = protocol
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(protocol)
        # set the time until a message times out
        self.client.set_option("messageTimeout", message_timeout)

    # Sends a message to an output queue, to be routed by IoT Edge hub.
    def send_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)


def main(imagePath, imageProcessingEndpoint):
    # If file exists on the imagePath, then use oldest file and delete it.
    # If file does not exist, to do nothing.

    try:
        print("File capture module for Azure IoT Edge. Press Ctrl-C to exit")

        try:
            global hubManager
            hubManager = HubManager(PROTOCOL, MESSAGE_TIMEOUT)
        except IoTHubError as iothub_error:
            print("Unexpected error %s from IoTHub" % iothub_error)
            return

        # check file existence
        if Path(imagePath).exists:
            dir = Path(imagePath)
        else:
            return

        print("The sample is now sendint images for processing and will indefinitely.")
        while True:
            # classification, send to hub, delete file
            for f in dir.iterdir():
                print("Target files : %s " % f)
                classification = sendFrameForProcessing(
                    str(f), imageProcessingEndpoint)
                send_to_hub(classification)
                time.sleep(10)
                os.remove(str(f))

    except KeyboardInterrupt:
        print("IoT Edge module sample stopped")


if __name__ == '__main__':
    try:
        # Retrieve the image location and image classifying server endpoint from container environment
        IMAGE_PATH = os.getenv('IMAGE_PATH', "")
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")
    except ValueError as error:
        print(error)
        sys.exit(1)

    if ((IMAGE_PATH and IMAGE_PROCESSING_ENDPOINT) != ""):
        main(IMAGE_PATH, IMAGE_PROCESSING_ENDPOINT)
    else:
        print("Error: Image path or image-processing endpoint missing")
