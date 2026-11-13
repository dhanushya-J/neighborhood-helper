import sys
import os

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_database

if __name__ == '__main__':
    force = '--force' in sys.argv
    print(f"Initializing Neighborhood Helper Database (force={force})...")
    try:
        init_database(force=force)
        print("Done!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
