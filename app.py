from flask import Flask
from datamanager.sqlite_data_manager import SQLiteDataManager, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_manager = SQLiteDataManager(app)

@app.route('/')
def home():
    return "Welcome to MovieWeb App!"

if __name__ == '__main__':
    app.run(debug=True)