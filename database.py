import sqlite3
import threading
from contextlib import contextmanager

DB_NAME = "bot.db"

class Database:
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self._create_tables()

    def conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(DB_NAME)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    @contextmanager
    def cur(self):
        conn = self.conn()
        c = conn.cursor()
        try:
            yield c
            conn.commit()
        finally:
            c.close()

    def _create_tables(self):
        with self.cur() as c:
            c.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY,
                    title TEXT
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    group_id INTEGER
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS vip (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT,
                    type TEXT CHECK(type IN ('обычный', 'глобальный'))
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS selected (
                    owner_id INTEGER PRIMARY KEY,
                    group_id INTEGER
                )
            ''')
            c.execute('INSERT OR IGNORE INTO selected (owner_id) VALUES (?)', (OWNER_ID,))

db = Database()