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
            'id_account' : '',
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

                resp['id_account'] = data[0]
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
            id_account = request.form['id_account'] # pake id doang, bukan id_account
            image = request.files['image']

            date_now_yyyymmdd = datetime.datetime.now().strftime("%Y-%m-%d")
            time_now_hhmmss = datetime.datetime.now().strftime("%H:%M:%S")

            
            resp = {
                'status' : '',
                'message': ''
            }

            account_search = detect_account(id_account)
            if account_search != 'account_ditemukan':
                resp['status'] = 'failed'
                resp['message'] = account_search
                return jsonify(resp)
            
            cursor = mysql.connection.cursor()
            
            # cek apakah sudah absen hari ini
            cursor.execute("SELECT * FROM present JOIN detail_attendance ON present.id = detail_attendance.id_attendance WHERE detail_attendance.id_account = %s AND detail_attendance.date = %s AND present.clock_in IS NOT NULL", (id_account, date_now_yyyymmdd))

            data = cursor.fetchone()

            print('DATA : ' + str(data))

            if data is None:

                # check directory
                if not os.path.exists('app/storage/new_data/' + id_account):
                    os.makedirs('app/storage/present_image/new_data/' + id_account)

                # save image
                image.save('app/storage/present_image/new_data/' + id_account + '/' + date_now_yyyymmdd + 'clock_in.jpg')

                image_path = 'app/storage/new_data/' + id_account + '/' + date_now_yyyymmdd + 'clock_in.jpg'


                # masukin data ke tabel present dulu buat dapetin id attendance nya
                cursor.execute("INSERT INTO present (date, clock_in, clock_out, image) VALUES (%s, %s, %s, %s)", (date_now_yyyymmdd, time_now_hhmmss, '-', image_path))
                
                last_id = cursor.lastrowid

                # masukin data ke tabel detail_attendance dengan membawa id attendance yang baru saja didapat
                cursor.execute("INSERT INTO detail_attendance (date, id_account, id_attendance) VALUES (%s, %s, %s)", (date_now_yyyymmdd, id_account, last_id))

                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil Clock In'
            
            else:
                cursor.execute("UPDATE present SET clock_out = %s WHERE id = %s", (time_now_hhmmss, data[0]))

                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil Clock Out'

            mysql.connection.commit()
            cursor.close()


            return jsonify(resp)
            