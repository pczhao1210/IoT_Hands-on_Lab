from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
import psycopg2 as pg
app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    conn = pg.connect(database = "iotdata", user="postgres", password="postgres", host="139.217.82.19", port="5432")
    cur = conn.cursor()
    sql = 'SELECT * FROM public.aiot ORDER BY "time" Desc LIMIT 50'
    cur.execute(sql)
    u = cur.fetchall()
    conn.close()
    return render_template('index.html',u=u)
if __name__ == '__main__':
    app.run(host='0.0.0.0')