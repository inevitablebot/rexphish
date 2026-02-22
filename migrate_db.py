import sqlite3

def migrate():
    conn = sqlite3.connect('instance/site.db') # Flask-SQLAlchemy default location usually instance/site.db or just site.db
    # Check if instance/site.db exists, else check site.db
    import os
    if not os.path.exists('instance/site.db'):
        if os.path.exists('site.db'):
            conn = sqlite3.connect('site.db')
        else:
            print("Database not found!")
            return

    cursor = conn.cursor()
    
    columns = [
        ('sender_email', 'VARCHAR(120)'),
        ('sender_password', 'VARCHAR(120)'),
        ('subject', 'VARCHAR(200)'),
        ('body', 'TEXT'),
        ('host_url', 'VARCHAR(200)')
    ]
    
    for col_name, col_type in columns:
        try:
            cursor.execute(f"ALTER TABLE campaign ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError as e:
            if 'duplicate column' in str(e):
                print(f"Column {col_name} already exists")
            else:
                print(f"Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
