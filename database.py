import sqlite3
import sys 
from PyQt5.QtWidgets import QMessageBox

class DatabaseManager:
    def __init__(self):
        self.database_filename = 'data.db'
        self.connect_to_file()

    def _handle_query_error(self):
        QMessageBox.warning(None, "ERROR 303", "Something went wrong with the database")

    def connect_to_file(self):
        try:
            self.connection = sqlite3.connect(self.database_filename)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(e)
            sys.exit(1)            

    def fetch_data(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(e)
            self._handle_query_error()

    def fetch_all_data(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            
            return self.cursor.fetchall()
        
        except sqlite3.Error as e:
            print(e)
            self._handle_query_error()

    def insert_data(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)
            self._handle_query_error()
    
    def delete_data(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)
            self._handle_query_error()
        
    def close_connection(self):
        self.cursor.close()
        self.connection.close()



class Sqlite:
    def __init__(self):
        self.db = DatabaseManager()

    def insert_data_sqlite(self, table_name, sqlite_database_columns, product_data):
        columns = ", ".join(sqlite_database_columns)
        placeholders = ", ".join("?" * len(sqlite_database_columns))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.db.insert_data(query, product_data)
        

    def fetch_data_sqlite(self, table_name, columns_to_fetch_data_from):
        columns_to_fetch_data_from = ", ".join(columns_to_fetch_data_from)
        query = f"SELECT {columns_to_fetch_data_from} FROM {table_name}"
        all_data = self.db.fetch_all_data(query)

        return all_data

