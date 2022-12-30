from flask import request, jsonify 
import os
import datetime
from app.helper.account_helper import detect_account
from app.main import deploy

app = deploy()[0]
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
            'unique_account_id' : '',
            'status' : '',
            'message': '',
            # 'token': ''
        }

        # print('I FOUND : ' + str(data))

        if data is None:
            resp['status'] = 'failed'
            resp['message'] = 'Anda tidak terdaftar'
            return resp
        else:
            if password == data[3] and username == data[2]:

                
                print('I FOUND : ' + str(data))
                print('===============================')
                print('USERNAME : ' + str(data[2]))
                print('ID ACCOUNT : ' + str(data[1]))
                print('===============================')

                resp['unique_account_id'] = data[0]
                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil login'

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
            unique_account_id = request.form['unique_account_id'] # pake id doang, bukan unique_account_id
            image = request.files['image']

            date_now_yyyymmdd = datetime.datetime.now().strftime("%Y-%m-%d")
            time_now_hhmmss = datetime.datetime.now().strftime("%H:%M:%S")

            
            resp = {
                'status' : '',
                'message': ''
            }

            account_search = detect_account(unique_account_id)
            if account_search != 'account_ditemukan':
                resp['status'] = 'failed'
                resp['message'] = account_search
                return jsonify(resp)
            
            cursor = mysql.connection.cursor()
            
            # cek apakah sudah absen hari ini
            cursor.execute("SELECT * FROM present JOIN detail_attendance ON present.id = detail_attendance.id_attendance WHERE detail_attendance.unique_account_id = %s AND detail_attendance.date = %s AND present.clock_in IS NOT NULL", (unique_account_id, date_now_yyyymmdd))

            data = cursor.fetchone()

            print('DATA : ' + str(data))

            if data is None:

                # check directory
                if not os.path.exists('app/storage/new_data/' + unique_account_id):
                    os.makedirs('app/storage/present_image/new_data/' + unique_account_id)

                # save image
                image.save('app/storage/present_image/new_data/' + unique_account_id + '/' + date_now_yyyymmdd + 'clock_in.jpg')

                image_path = 'app/storage/new_data/' + unique_account_id + '/' + date_now_yyyymmdd + 'clock_in.jpg'


                # masukin data ke tabel present dulu buat dapetin id attendance nya
                cursor.execute("INSERT INTO present (date, clock_in, clock_out, absence_image_path) VALUES (%s, %s, %s, %s)", (date_now_yyyymmdd, time_now_hhmmss, '-', image_path))
                
                last_id = cursor.lastrowid

                # masukin data ke tabel detail_attendance dengan membawa id attendance yang baru saja didapat
                cursor.execute("INSERT INTO detail_attendance (date, unique_account_id, id_attendance) VALUES (%s, %s, %s)", (date_now_yyyymmdd, unique_account_id, last_id))

                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil Clock In'
            
            else:
                cursor.execute("UPDATE present SET clock_out = %s WHERE id = %s", (time_now_hhmmss, data[0]))

                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil Clock Out'

            mysql.connection.commit()
            cursor.close()


            return jsonify(resp)
            