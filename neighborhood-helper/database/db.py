import os
import pymysql
from pymysql.cursors import DictCursor
from flask import g, current_app
from config import Config

def get_raw_connection(include_database=True):
    """Establishes a raw PyMySQL connection."""
    kwargs = {
        'host': Config.MYSQL_HOST,
        'port': Config.MYSQL_PORT,
        'user': Config.MYSQL_USER,
        'password': Config.MYSQL_PASSWORD,
        'charset': 'utf8mb4',
        'cursorclass': DictCursor,
        'autocommit': True
    }
    if include_database:
        kwargs['database'] = Config.MYSQL_DB
    return pymysql.connect(**kwargs)

def get_db():
    """Gets or creates the database connection for the current Flask request context."""
    if 'db' not in g:
        g.db = get_raw_connection(include_database=True)
    return g.db

def close_db(e=None):
    """Closes the request-level database connection."""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def query_db(query, args=None, one=False):
    """Executes a SELECT query using parameterized arguments and returns DictCursor rows."""
    db = get_db()
    with db.cursor() as cursor:
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv

def execute_db(query, args=None):
    """Executes an INSERT, UPDATE, or DELETE query and returns the lastrowid and affected rows."""
    db = get_db()
    with db.cursor() as cursor:
        if args:
            affected = cursor.execute(query, args)
        else:
            affected = cursor.execute(query)
        last_id = cursor.lastrowid
        return {'last_id': last_id, 'affected': affected}

def init_database(force=False):
    """Initializes the database schema and seed data if needed."""
    # First connect without database to ensure database exists
    conn = get_raw_connection(include_database=False)
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    finally:
        conn.close()

    # Now connect to the database
    conn = get_raw_connection(include_database=True)
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'users';")
            exists = cur.fetchone()
            if exists and not force:
                print(f"[DB] Database '{Config.MYSQL_DB}' is already initialized.")
                return

        # Execute schema
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, 'schema.sql')
        seed_path = os.path.join(base_dir, 'seed.sql')

        print(f"[DB] Running schema: {schema_path}")
        _execute_sql_file(conn, schema_path)

        print(f"[DB] Running seed data: {seed_path}")
        _execute_sql_file(conn, seed_path)

        # Refresh helper review statistics
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE helpers h
                SET 
                    avg_rating = COALESCE((SELECT ROUND(AVG(rating), 2) FROM reviews WHERE helper_id = h.id), 0.00),
                    total_reviews = (SELECT COUNT(*) FROM reviews WHERE helper_id = h.id);
            """)

        print(f"[DB] Database '{Config.MYSQL_DB}' initialized successfully with realistic demo data.")
    finally:
        conn.close()

def _execute_sql_file(conn, filepath):
    """Parses and executes multi-statement SQL script file safely."""
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Remove comments and split by semicolon
    statements = []
    current_stmt = []
    in_comment = False

    for line in sql.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith('--') or trimmed.startswith('/*'):
            continue
        current_stmt.append(line)
        if trimmed.endswith(';'):
            stmt = '\n'.join(current_stmt).strip()
            if stmt:
                statements.append(stmt)
            current_stmt = []

    with conn.cursor() as cur:
        for stmt in statements:
            # Skip USE statement since we are already connected to the DB
            if stmt.upper().startswith('USE '):
                continue
            try:
                cur.execute(stmt)
            except Exception as e:
                print(f"[DB WARNING] Failed statement: {stmt[:60]}... Error: {e}")
