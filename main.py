from flask import request, jsonify 
import jwt
import datetime
from dotenv import load_dotenv
from app.helper.account_helper import detect_account
from app.main import deploy

load_dotenv()

app = deploy()[0]
# initiate koneksi ke database menggunakan config yang sudah di prepare
mysql = deploy()[1]



# List of routes (endpoints) start by @
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


@app.route('/do_absen', methods = ['POST', 'GET'])
def do_absen():
    
        if request.method == 'GET':
            return "Absen via the Absen Form"
    
        if request.method == 'POST':
            id_account = request.json['id_account']
            status = request.json['status']
            token = request.json['token']
            date_now_yyyymmdd = datetime.datetime.now().strftime("%Y-%m-%d")
            time_now_hhmmss = datetime.datetime.now().strftime("%H:%M:%S")
    
            try:
                jwt.decode(token, app.config['SECRET_KEY'])
            except:
                return jsonify({'status': 'failed', 'message': 'Token tidak valid'})
            
            resp = {
                'status' : '',
                'message': ''
            }

            account_search = detect_account(id_account, token)
            if account_search != 'account_ditemukan':
                resp['status'] = 'failed'
                resp['message'] = account_search
                return jsonify(resp)
            
            cursor = mysql.connection.cursor()
            
            # cek apakah sudah absen hari ini
            cursor.execute("SELECT * FROM present JOIN detail_attendance ON present.id = detail_attendance.id_attendance WHERE detail_attendance.id_account = %s AND detail_attendance.date = %s AND present.clock_in IS NOT NULL", (id_account, date_now_yyyymmdd))

            data = cursor.fetchone()

            if data is not None:
                
                cursor.execute("INSERT INTO present (date, clock_in, clock_out, image) VALUES (%s, %s, %s, %s)", (date_now_yyyymmdd,id_account, status))
                last_id = cursor.lastrowid

                cursor.execute("INSERT INTO detail_attendance (id_detail_attendance, date, id_account, id_attendance) VALUES (%s, %s, %s, %s)", (date_now_yyyymmdd, id_account, status))

                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil Clock In'
            
            else:
                cursor.execute("UPDATE present SET clock_out = %s WHERE id = %s", (time_now_hhmmss, data[0]))
                cursor.execute("UPDATE detail_attendance SET status = %s WHERE id_detail_attendance = %s", (status, data[0]))

                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil Clock Out'

            mysql.connection.commit()
            cursor.close()


            return jsonify(resp)
            