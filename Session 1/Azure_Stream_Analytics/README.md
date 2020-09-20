Please use this query to calculate the value of past 10 seconds from IoT Hub then output to Azure Function.

```
SELECT
    System.Timestamp() AS Time,
    IoTHub.ConnectionDeviceId as DeviceID,
    AVG(CAST(Voltage AS FLOAT)) AS Voltage,
    AVG(CAST(Ampere AS FLOAT)) AS Ampere,
    AVG(CAST(Walt AS FLOAT)) AS KWalt
INTO
    YOUR_OUTPUT_BINDING_NAME
FROM
    YOUR_INPUT_BINDING_NAME TIMESTAMP BY EventEnqueuedUtcTime
GROUP BY
    IoTHub.ConnectionDeviceId,
    TumblingWindow(second, 10)

```