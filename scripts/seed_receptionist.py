import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect('clinova-dev.db')
c = conn.cursor()

c.execute("SELECT id FROM users WHERE username = 'receptionist' OR id = 'usr-rec-08'")
existing = c.fetchone()

if not existing:
    c.execute("SELECT hashed_password FROM users WHERE username = 'nurse'")
    nurse_hash_row = c.fetchone()
    pwd_hash = nurse_hash_row[0] if nurse_hash_row else "$2b$12$eXampleHashPlaceHolderForDevEnvironmentOnly"

    now_iso = datetime.now(timezone.utc).isoformat()
    c.execute("""
        INSERT INTO users (
            id, email, full_name, role, facility_id, is_active, created_at, username, hashed_password
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'usr-rec-08',
        'tunde.olawale@clinova.internal',
        'Tunde Olawale',
        'RECEPTIONIST',
        'FAC-DH-04',
        1,
        now_iso,
        'receptionist',
        pwd_hash
    ))
    conn.commit()
    print("Successfully seeded usr-rec-08 (Tunde Olawale, RECEPTIONIST).")
else:
    print("Receptionist already exists in database.")

conn.close()
