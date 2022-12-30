from flask import Flask
from flask_mysqldb import MySQL 
from app.config.database import get_db_config


def deploy():
  app = Flask(__name__)

  # prepare credential untuk Inisiasi koneksi ke database, modular styleee baby!
  for key, value in get_db_config().items():
      app.config[key] = value

  # initiate koneksi ke database menggunakan config yang sudah di prepare
  mysql = MySQL(app)
  return app, mysql