import sqlite3
from sqlite3 import Error
import threading

# This ensures that only one thread can
# write/commit changes to the database at a time.
# Gotta avoid those race conditions.
db_lock = threading.Lock()

def connect_to_db():
    try:
        connection = sqlite3.connect('bot_database.db', check_same_thread=False)
        connection.execute("""
                    CREATE TABLE IF NOT EXISTS approved_users (
                        username TEXT NOT NULL
                    );
                    """)
        
        connection.execute("""
                    CREATE TABLE IF NOT EXISTS restricted_subreddits (
                        subreddit_name TEXT NOT NULL
                    );
                    """)
        
        connection.execute("""
                    CREATE TABLE IF NOT EXISTS request_posts (
                        post_id TEXT NOT NULL
                    );
                    """)

        return connection
    except Error as e:
        print(e)
        raise

# --------------------------------------------
# CRUD operations for managing approved users.
# --------------------------------------------
def insert_approved_user(connection, username):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM approved_users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if not result:
        with db_lock:
            connection.execute("INSERT INTO approved_users (username) VALUES (?)", (username,))
            connection.commit()

def retrieve_approved_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM approved_users")

    return cursor.fetchall()

def remove_approved_user(connection, username):
    with db_lock:
        connection.execute("DELETE FROM approved_users WHERE username = ?", (username,))
        connection.commit()

# ---------------------------------------------------
# CRUD operations for managing restricted subreddits.
# ---------------------------------------------------
def insert_restricted_subreddit(connection, sub_name):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM restricted_subreddits WHERE subreddit_name = ?", (sub_name,))
    result = cursor.fetchone()

    if not result:
        with db_lock:
            connection.execute("INSERT INTO restricted_subreddits (subreddit_name) VALUES (?)", (sub_name,))
            connection.commit()

def retrieve_restricted_subreddits(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM restricted_subreddits")

    return cursor.fetchall()

def remove_restricted_subreddit(connection, sub_name):
    with db_lock:
        connection.execute("DELETE FROM restricted_subreddits WHERE subreddit_name = ?", (sub_name,))
        connection.commit()

# -------------------------------------------
# CRUD operations for managing request posts.
# -------------------------------------------
def insert_request_post(connection, post):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM request_posts WHERE post_id = ?", (post.id,))
    result = cursor.fetchone()

    if not result:
        with db_lock:
            connection.execute("INSERT INTO request_posts (post_id) VALUES (?)", (post.id,))
            connection.commit()

def retrieve_request_posts(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM request_posts")

    return cursor.fetchall()

def remove_request_post(connection, post):
    with db_lock:
        connection.execute("DELETE FROM request_posts WHERE post_id = ?", (post.id,))
        connection.commit()

# Self-explanatory. This comment isn't needed, but I ain't deleting it.
def close_connection(connection):
    connection.close()