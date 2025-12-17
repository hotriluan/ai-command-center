"""
Check and kill locks on sales_data table
"""
from database import engine

connection = engine.raw_connection()
cursor = connection.cursor()

try:
    # Show processlist to see what's locking
    print("Checking for locks on sales_data table...\n")
    cursor.execute("SHOW PROCESSLIST")
    
    print("Active processes:")
    print(f"{'ID':<10} {'User':<15} {'Host':<20} {'DB':<15} {'Command':<15} {'Time':<10} {'State':<30}")
    print("=" * 120)
    
    processes_to_kill = []
    for row in cursor.fetchall():
        process_id, user, host, db, command, time, state, info = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7] if len(row) > 7 else None
        print(f"{process_id:<10} {user:<15} {host:<20} {db or '':<15} {command:<15} {time:<10} {state or '':<30}")
        
        # Look for processes that might be locking the table
        if info and 'sales_data' in str(info).lower() and command != 'Sleep':
            if 'ALTER TABLE' in str(info) or 'ADD COLUMN' in str(info):
                processes_to_kill.append(process_id)
                print(f"  ⚠️  This process is likely locking sales_data: {info[:100]}")
    
    if processes_to_kill:
        print(f"\n\nFound {len(processes_to_kill)} process(es) to kill: {processes_to_kill}")
        response = input("\nDo you want to kill these processes? (yes/no): ")
        
        if response.lower() == 'yes':
            for pid in processes_to_kill:
                try:
                    cursor.execute(f"KILL {pid}")
                    print(f"  ✅ Killed process {pid}")
                except Exception as e:
                    print(f"  ❌ Failed to kill process {pid}: {e}")
            connection.commit()
            print("\n✅ Processes killed. You can now retry the table recreation.")
        else:
            print("\nNo processes killed.")
    else:
        print("\n✅ No blocking processes found.")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    cursor.close()
    connection.close()
