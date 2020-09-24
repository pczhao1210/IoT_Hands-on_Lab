
module.exports={
 
    /*
    *  Execute a sql query
    */
   opt_pg: async function  (context,sqlstatement) {

        const client = require('pg');
       
        console.log("Executing the sql: " + sqlstatement);

        const client = new Client({
            user: "postgres",
            database: "iotdata",
            password: "postgres",
            port: 5432,
            host: "139.217.82.19",
        });

        try {
            await client.connect(Client)
            const result = await client.query(sqlstatement)
            context.res = { body: result}
        }
        catch (error) {
            console.log(error) 
            context.res = { body: error, status: 500}
        }   
       
    }


};