import base64
import hmac
import hashlib

def print_twin(title, iothub_device):
    print(title + ":")
    print("device_id                      = {0}".format(iothub_device.device_id))
    print("module_id                      = {0}".format(iothub_device.module_id))
    print("authentication_type            = {0}".format(iothub_device.authentication_type))
    print("x509_thumbprint                = {0}".format(iothub_device.x509_thumbprint))
    print("etag                           = {0}".format(iothub_device.etag))
    print("device_etag                    = {0}".format(iothub_device.device_etag))
    print("tags                           = {0}".format(iothub_device.tags))
    print("version                        = {0}".format(iothub_device.version))

    print("status                         = {0}".format(iothub_device.status))
    print("status_reason                  = {0}".format(iothub_device.status_reason))
    print("status_update_time             = {0}".format(iothub_device.status_update_time))
    print("connection_state               = {0}".format(iothub_device.connection_state))
    print("last_activity_time             = {0}".format(iothub_device.last_activity_time))
    print(
        "cloud_to_device_message_count  = {0}".format(iothub_device.cloud_to_device_message_count)
    )
    print("device_scope                   = {0}".format(iothub_device.device_scope))

    print("properties                     = {0}".format(iothub_device.properties))
    print("additional_properties          = {0}".format(iothub_device.additional_properties))
    print("")


def print_query_result(title, query_result):
    print("")
    print("Type: {0}".format(query_result.type))
    print("Continuation token: {0}".format(query_result.continuation_token))
    if query_result.items:
        x = 1
        for d in query_result.items:
            print_twin("{0}: {0}".format(title, x), d)
            x += 1
    else:
        print("No item found")


def print_device_info(title, iothub_device):
    print(title + ":")
    print("device_id                      = {0}".format(iothub_device.device_id))
    print("authentication.type            = {0}".format(iothub_device.authentication.type))
    print("authentication.symmetric_key   = {0}".format(iothub_device.authentication.symmetric_key))
    print(
        "authentication.x509_thumbprint = {0}".format(iothub_device.authentication.x509_thumbprint)
    )
    print("connection_state               = {0}".format(iothub_device.connection_state))
    print(
        "connection_state_updated_tTime = {0}".format(iothub_device.connection_state_updated_time)
    )
    print(
        "cloud_to_device_message_count  = {0}".format(iothub_device.cloud_to_device_message_count)
    )
    print("device_scope                   = {0}".format(iothub_device.device_scope))
    print("etag                           = {0}".format(iothub_device.etag))
    print("generation_id                  = {0}".format(iothub_device.generation_id))
    print("last_activity_time             = {0}".format(iothub_device.last_activity_time))
    print("status                         = {0}".format(iothub_device.status))
    print("status_reason                  = {0}".format(iothub_device.status_reason))
    print("status_updated_time            = {0}".format(iothub_device.status_updated_time))
    print("")


def print_device_info_short(title, iothub_device):
    print(title + ":")
    print("device_id                      = {0}".format(iothub_device.device_id))
    #print("authentication.type            = {0}".format(iothub_device.authentication.type))
    #print("authentication.symmetric_key   = {0}".format(iothub_device.authentication.symmetric_key))
    #print(
    #    "authentication.x509_thumbprint = {0}".format(iothub_device.authentication.x509_thumbprint)
    #)
    print("connection_state               = {0}".format(iothub_device.connection_state))
    #print(
    #    "connection_state_updated_tTime = {0}".format(iothub_device.connection_state_updated_time)
    #)
    #print(
    #    "cloud_to_device_message_count  = {0}".format(iothub_device.cloud_to_device_message_count)
    #)
    #print("device_scope                   = {0}".format(iothub_device.device_scope))
    #print("etag                           = {0}".format(iothub_device.etag))
    #print("generation_id                  = {0}".format(iothub_device.generation_id))
    print("last_activity_time             = {0}".format(iothub_device.last_activity_time))
    print("status                         = {0}".format(iothub_device.status))
    #print("status_reason                  = {0}".format(iothub_device.status_reason))
    #print("status_updated_time            = {0}".format(iothub_device.status_updated_time))
    print("")


def derive_device_key(device_id, master_symmetric_key):
    message = device_id.encode("utf-8")
    #print(message)
    signing_key = base64.b64decode(master_symmetric_key.encode("utf-8"))
    #print(signing_key)
    signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
    #print(signed_hmac)
    device_key_encoded = base64.b64encode(signed_hmac.digest())
    #print(device_key_encoded)
    #print(device_key_encoded.decode("utf-8"))
    return device_key_encoded.decode("utf-8")