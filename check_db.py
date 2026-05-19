import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_backend.settings')
django.setup()

from django.db import connection

def check_database():
    print("=== Django Database Diagnostics ===")
    
    # Get database connection parameters
    settings_dict = connection.settings_dict
    print(f"Database Engine: {settings_dict.get('ENGINE')}")
    print(f"Database Name:   {settings_dict.get('NAME')}")
    print(f"Database User:   {settings_dict.get('USER')}")
    print(f"Database Host:   {settings_dict.get('HOST') or 'localhost (default)'}")
    print(f"Database Port:   {settings_dict.get('PORT') or '5432 (default)'}")
    
    try:
        # Check connection and query tables
        tables = connection.introspection.table_names()
        print("\n=== Connection Status ===")
        print("Successfully connected to the database!")
        print(f"Total tables found: {len(tables)}")
        
        # Check custom user table
        user_table = 'api_customuser'
        if user_table in tables:
            print(f"Found table: '{user_table}'")
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {user_table}")
                count = cursor.fetchone()[0]
                print(f"Total records in '{user_table}': {count}")
                
                # Print a few user emails to verify
                cursor.execute(f"SELECT email, role FROM {user_table} LIMIT 5")
                users = cursor.fetchall()
                print("Seeded Users in DB:")
                for email, role in users:
                    print(f"  - {email} ({role})")
        else:
            print(f"Warning: Table '{user_table}' not found in the tables list!")
            
        print("\nAll Available Tables:")
        for t in sorted(tables):
            print(f"  - {t}")
            
    except Exception as e:
        print("\n=== Connection Error ===")
        print(f"Failed to connect to the database: {str(e)}")

if __name__ == '__main__':
    check_database()
