import sqlite3
import os

def create_db_from_sql(db_filename, sql_filename):
    # Check if the SQL file actually exists before trying to read it
    if not os.path.exists(sql_filename):
        print(f"Error: The file '{sql_filename}' was not found.")
        return

    connection = None
    
    try:
        # 1. Read the contents of the SQL file
        with open(sql_filename, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        # 2. Connect to the database (this creates the .db file if it doesn't exist)
        connection = sqlite3.connect(db_filename)
        cursor = connection.cursor()

        # 3. Execute the entire script
        print(f"Executing '{sql_filename}'...")
        cursor.executescript(sql_script)
        
        # 4. Commit the changes
        connection.commit()
        print(f"Success! Database '{db_filename}' has been created and populated.")

    except sqlite3.Error as sqlite_error:
        print(f"An SQLite error occurred: {sqlite_error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # 5. Always ensure the connection is closed
        if connection:
            connection.close()

if __name__ == "__main__":
    # Replace these strings with your actual file names
    YOUR_SQL_FILE = r"D:\Project_2\data\prodapt-project\projectfiles\sql\02_seed_data.sql"
    YOUR_DB_NAME = "telecom_ops.db"
    
    create_db_from_sql(YOUR_DB_NAME, YOUR_SQL_FILE)