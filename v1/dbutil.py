import sqlite3
import os

class Database:
    def __init__(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)

        self.conn = sqlite3.connect(f'{script_dir}/crawldata.db')
        self.cursor = self.conn.cursor()
        #self.cursor.execute("drop table board_data")
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS board_data (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                board_num INTEGER NOT NULL
            )
        ''')
    
    def insertNum(self, number):
        self.cursor.execute('INSERT INTO board_data (board_num) VALUES (?)', (number,))
        self.conn.commit()

    def selectNum(self, number):
        self.cursor.execute('SELECT * FROM board_data WHERE board_num = ?', (number,))
        result = self.cursor.fetchone()
        return result is not None
    
    def __reduce__(self):
        self.conn.close()

