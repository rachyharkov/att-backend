from flask import Flask, request, jsonify
from flask_mysqldb import MySQL 
import os
import jwt
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
 
mysql = MySQL(app)

@app.route('/')
def index():
    return 'mantaapp'

@app.route('/login', methods = ['POST', 'GET'])
def login():

    if request.method == 'GET':
        return "Login via the login Form"

    if request.method == 'POST':
        username = request.json['usernamenya']
        password = request.json['passwordnya']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM account WHERE username = %s", (username,)) # <-- this is the problem, I think it's because of the comma
        data = cursor.fetchone()

        mysql.connection.commit()
        cursor.close()
        
        resp = {
            'id_account' : '',
            'status' : '',
            'message': '',
            'token': ''
        }

        # print('I FOUND : ' + str(data))

        if data is None:
            resp['status'] = 'failed'
            resp['message'] = 'Anda tidak terdaftar'
            return resp
        else:
            if password == data[3] and username == data[2]:

                token = jwt.encode({
                    'user' : username, 
                    'exp' : 'forever'
                }, app.config['SECRET_KEY'])
                
                print('I FOUND : ' + str(data))
                print('===============================')
                print('USERNAME : ' + str(data[2]))
                print('ID ACCOUNT : ' + str(data[1]))
                print('===============================')

                resp['id_account'] = data[0]
                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil login'
                resp['token'] = token
                return jsonify(resp)
            else:
                resp['status'] = 'failed'
                resp['message'] = 'Anda terdaftar, tapi data login salah, silahkan coba lagi'
                return jsonify(resp)