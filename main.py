from flask import Flask,render_template,request
from flask_mysqldb import MySQL 
import os

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
 
mysql = MySQL(app)

@app.route('/')
def index():
    return 'asdadsasad'

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        username = request.form['usernamenya']
        idaccount = request.form['idaccountnya']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM account WHERE username = %s AND id_account = %s", (username, idaccount))
        data = cursor.fetchone()

        mysql.connection.commit()
        cursor.close()
        
        print('I FOUND : ' + str(data))
        print('===============================')
        print('USERNAME : ' + str(data[2]))
        print('ID ACCOUNT : ' + str(data[1]))
        print('===============================')

        if data is None:
            return "Invalid username or password"
        else:
            return "Login Success"