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

@app.route('/do_absen', methods = ['POST', 'GET'])
def do_absen():
    
    if request.method == 'GET':
        return "Absen via the Absen Form"

    if request.method == 'POST':
        user_id = request.form['user_id'] # pake id doang, bukan user_id
        image = request.files['image']

        date_now_yyyymmdd = datetime.datetime.now().strftime("%Y-%m-%d")
        time_now_hhmmss = datetime.datetime.now().strftime("%H:%M:%S")

        
        resp = {
            'status' : '',
            'message': ''
        }

        account_search = detect_account(user_id)
        if account_search == 'account_not_found':
            resp['status'] = 'failed'
            resp['message'] = account_search
            return jsonify(resp)
        
        cursor = mysql.connection.cursor()
        
        # cek apakah sudah absen hari ini
        cursor.execute("SELECT * FROM present JOIN detail_attendance ON present.id = detail_attendance.id_attendance WHERE detail_attendance.user_id = %s AND detail_attendance.date = %s AND present.clock_in IS NOT NULL", (user_id, date_now_yyyymmdd))

        data = cursor.fetchone()

        print('DATA : ' + str(data))

        # jika belum absen hari ini, kan data ga ada tuh? jadi data = None, otw buat data
        if data is None:

            # check directory
            if not os.path.exists('app/storage/new_data/' + user_id):
                os.makedirs('app/storage/present_image/new_data/' + user_id)

            # save image
            image.save('app/storage/present_image/new_data/' + user_id + '/' + date_now_yyyymmdd + 'clock_in.jpg')

            image_path = 'app/storage/new_data/' + user_id + '/' + date_now_yyyymmdd + 'clock_in.jpg'
            # ======================================================== #

            machine_learning_result = '1' # ini hasil return dari machine learning, harusnya dibuat function, isinya proses2 machine learningnya (gw saranin ml taro di folder app)

            # misalnya: machine_learning_result = detect_face(image_path)
            # ======================================================== #
            if machine_learning_result == user_id:
                print('MATCH!')
                # masukin data ke tabel present dulu buat dapetin id attendance nya
                cursor.execute("INSERT INTO present (date, clock_in, clock_out, absence_image_path) VALUES (%s, %s, %s, %s)", (date_now_yyyymmdd, time_now_hhmmss, '-', image_path))
                
                last_id = cursor.lastrowid

                # masukin data ke tabel detail_attendance dengan membawa id attendance yang baru saja didapat
                cursor.execute("INSERT INTO detail_attendance (date, user_id, id_attendance) VALUES (%s, %s, %s)", (date_now_yyyymmdd, user_id, last_id))

                resp['status'] = 'success'
                resp['message'] = 'Anda berhasil Clock In'
            else:
                print('NOT MATCH!')
                resp['status'] = 'failed'
                resp['message'] = 'Anda tidak berhasil Clock In, karena tidak sesuai dengan data yang ada'

            
        
        else: # jika sudah absen hari ini, maka data ada, otw update data
            cursor.execute("UPDATE present SET clock_out = %s WHERE id = %s", (time_now_hhmmss, data[0]))

            resp['status'] = 'success'
            resp['message'] = 'Anda berhasil Clock Out'

        mysql.connection.commit()
        cursor.close()

        return jsonify(resp)
        