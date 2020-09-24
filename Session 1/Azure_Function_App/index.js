module.exports = async function (context, eventHubMessages) {
    
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
           
    var service = require('./optpg');
    await service.opt_pg(context, queryString);
          
    });
};