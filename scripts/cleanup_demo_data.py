"""CLINOVA AI — Safe Scoped Demonstration Data Cleanup.

Safely prunes leftover test-run artifacts and unlinked test personas
while strictly preserving:
- Canonical fixed-role accounts (usr-doc-01, usr-nurse-02, usr-rec-08, etc.)
- Healthcare facilities and capabilities
- Active clinical cases and patient records
- Tamper-evident cryptographic audit log chains
"""

import sqlite3
import sys

def run_scoped_cleanup(db_path: str = "clinova-dev.db"):
    print(f"Connecting to database: {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. Count unlinked test users
    c.execute("SELECT count(*) FROM users WHERE username LIKE 'unlinked_pt_%' AND patient_id IS NULL")
    orphan_count = c.fetchone()[0]
    print(f"Found {orphan_count} orphan unlinked test user accounts.")

    if orphan_count > 0:
        c.execute("DELETE FROM users WHERE username LIKE 'unlinked_pt_%' AND patient_id IS NULL")
        conn.commit()
        print(f"Successfully pruned {orphan_count} orphan test user accounts.")
    else:
        print("No orphan test accounts found.")

    # 2. Verify canonical seed personas are intact
    c.execute("SELECT id, username, role, facility_id, is_active FROM users ORDER BY role")
    remaining_users = c.fetchall()
    print(f"\nRemaining canonical active users ({len(remaining_users)}):")
    for u in remaining_users:
        print(f"  {u[0]} ({u[1]}): {u[2]} at {u[3] or 'GLOBAL'} [Active: {bool(u[4])}]")

    # 3. Verify facilities are intact
    c.execute("SELECT id, facility_code, name, tier FROM facilities")
    facilities = c.fetchall()
    print(f"\nHealthcare facilities intact ({len(facilities)}):")
    for fac in facilities:
        print(f"  {fac[0]}: {fac[2]} ({fac[3]})")

    conn.close()
    print("\nScoped demonstration data cleanup completed safely.")

if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else "clinova-dev.db"
    run_scoped_cleanup(db_file)
