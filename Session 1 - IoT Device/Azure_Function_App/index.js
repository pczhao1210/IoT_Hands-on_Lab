module.exports = async function (context, eventHubMessages) {

    const { Client } = require('pg');

    const client = new Client({
        user: "postgres",
        database: "iotdata",
        password: "postgres",
        port: 5432,
        host: "139.217.82.19",
    });
    
    client.connect();
    
    context.log(`JavaScript eventhub trigger function called for message array ${JSON.stringify(eventHubMessages)}`);
    
    eventHubMessages.forEach(element => {
        context.log(`Get Message From Device '${JSON.stringify(element.DeviceID)}'`);
    
        const queryString = `INSERT INTO aiot(
            time, deviceid, voltage, ampere, kwalt
            ) VALUES(
            '${(element.Time)}',
            '${(element.DeviceID)}',
            '${(element.Voltage)}',
            '${(element.Ampere)}',
            '${(element.KWalt)}'
            )`;
        
        //context.log(queryString)
           
        client.query(queryString, (err, res) => {
            if (err) {
                context.log('Failed to Write to SQL');
                return;
            } else {
                context.log('Data insert successful');
                client.end();}
        });
          
    });
};
