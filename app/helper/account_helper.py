from app.main import deploy

def detect_account(id_account, token):
    mysql = deploy()[1]
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM account WHERE id_account = %s", (id_account,))
    data = cursor.fetchone()
    if data is None:
        return 'account_not_found'
    
    if token != data[4]:
        return 'token_not_valid'
    
    return 'account_ditemukan'
