import sqlite3
import hashlib
from getpass import getpass

DB_NAME = "A2_08_24.db"


# -------------------- Database Setup --------------------
def setup_database():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES accounts (id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        changed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        change_type TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks (id),
        FOREIGN KEY (user_id) REFERENCES accounts (id)
    )
    """)

    conn.commit()
    conn.close()


# -------------------- Utility Functions --------------------
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def print_table(headers, rows):
    """Print data in a simple table format without external libraries"""
    if not rows:
        print("No data found!")
        return

    rows_str = []
    for row in rows:
        rows_str.append([str(item) if item is not None else "" for item in row])

    col_widths = []
    for i in range(len(headers)):
        max_len = len(headers[i])
        for row in rows_str:
            max_len = max(max_len, len(row[i]))
        col_widths.append(max_len)

    line = "+".join("-" * (w + 2) for w in col_widths)

    print(line)
    header_row = " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers)))
    print(header_row)
    print(line)

    for row in rows_str:
        print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(row))))

    print(line)


# -------------------- User Functions --------------------
def register():
    """Create new user account"""
    print("\n---- Register New Account ----")
    username = input("Username: ").strip()
    password = getpass("Password: ")
    confirm = getpass("Confirm password: ")

    if not username:
        print("Username cannot be empty!")
        return False

    if password != confirm:
        print("Passwords don't match!")
        return False

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    try:
        hashed_pw = hash_password(password)
        cur.execute(
            "INSERT INTO accounts (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )
        conn.commit()
        print(f"Account '{username}' created successfully!")
        return True
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists!")
        return False
    finally:
        conn.close()


def login():
    """Log in to account"""
    print("\n---- Login ----")
    username = input("Username: ").strip()
    password = getpass("Password: ")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    hashed_pw = hash_password(password)
    cur.execute(
        "SELECT id FROM accounts WHERE username = ? AND password = ?",
        (username, hashed_pw)
    )
    result = cur.fetchone()
    conn.close()

    if result:
        print(f"Welcome back, {username}!")
        return result[0], username
    else:
        print("Login failed!")
        return None, None


def logout():
    """End user session"""
    print("Logged out!")


# -------------------- Task Functions --------------------
def add_task(user_id):
    """Add a new task"""
    print("\n---- Add New Task ----")
    name = input("Task name: ").strip()
    description = input("Description (optional): ").strip()

    if not name:
        print("Task name cannot be empty!")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks (user_id, name, description) VALUES (?, ?, ?)",
        (user_id, name, description)
    )
    task_id = cur.lastrowid

    cur.execute(
        """INSERT INTO history
        (task_id, user_id, name, description, status, change_type)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (task_id, user_id, name, description, "pending", "created")
    )

    conn.commit()
    conn.close()
    print(f"Task '{name}' added successfully!")


def show_tasks(user_id, all_tasks=False):
    """Display tasks"""
    print("\n---- My Tasks ----")
    if all_tasks:
        print("(Showing all tasks)")
    else:
        print("(Showing pending tasks)")

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if all_tasks:
        cur.execute("""
            SELECT id, name, description, status, created_date
            FROM tasks
            WHERE user_id = ?
            ORDER BY status, created_date DESC
        """, (user_id,))
    else:
        cur.execute("""
            SELECT id, name, description, status, created_date
            FROM tasks
            WHERE user_id = ? AND status != 'completed'
            ORDER BY created_date DESC
        """, (user_id,))

    tasks = cur.fetchall()
    conn.close()

    if not tasks:
        print("No tasks found!")
        return

    rows = []
    for task in tasks:
        task_id, name, desc, status, date = task
        if desc and len(desc) > 20:
            desc = desc[:17] + "..."
        rows.append([task_id, name, desc if desc else "", status, date])

    headers = ["ID", "Task", "Description", "Status", "Created"]
    print_table(headers, rows)


def edit_task(user_id):
    """Edit a task"""
    print("\n---- Edit Task ----")
    show_tasks(user_id, True)

    task_id = input("\nEnter task ID to edit (or press Enter to cancel): ").strip()
    if not task_id:
        print("Cancelled.")
        return

    try:
        task_id = int(task_id)
    except ValueError:
        print("Invalid ID!")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT name, description, status FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    task = cur.fetchone()

    if not task:
        print(f"Task #{task_id} not found!")
        conn.close()
        return

    curr_name, curr_desc, curr_status = task

    print(f"\nCurrent name: {curr_name}")
    print(f"Current description: {curr_desc if curr_desc else ''}")

    new_name = input("New name (press Enter to keep current): ").strip()
    new_desc = input("New description (press Enter to keep current): ").strip()

    if not new_name:
        new_name = curr_name
    if not new_desc:
        new_desc = curr_desc

    cur.execute(
        "UPDATE tasks SET name = ?, description = ? WHERE id = ?",
        (new_name, new_desc, task_id)
    )

    cur.execute(
        """INSERT INTO history
        (task_id, user_id, name, description, status, change_type)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (task_id, user_id, new_name, new_desc, curr_status, "updated")
    )

    conn.commit()
    conn.close()
    print(f"Task #{task_id} updated successfully!")


def complete_task(user_id):
    """Mark task as complete"""
    print("\n---- Complete Task ----")
    show_tasks(user_id, False)

    task_id = input("\nEnter task ID to complete (or press Enter to cancel): ").strip()
    if not task_id:
        print("Cancelled.")
        return

    try:
        task_id = int(task_id)
    except ValueError:
        print("Invalid ID!")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT name, description FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    task = cur.fetchone()

    if not task:
        print(f"Task #{task_id} not found!")
        conn.close()
        return

    name, desc = task

    cur.execute(
        "UPDATE tasks SET status = 'completed' WHERE id = ?",
        (task_id,)
    )

    cur.execute(
        """INSERT INTO history
        (task_id, user_id, name, description, status, change_type)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (task_id, user_id, name, desc, "completed", "completed")
    )

    conn.commit()
    conn.close()
    print(f"Task #{task_id} marked as completed!")


def delete_task(user_id):
    """Delete a task"""
    print("\n---- Delete Task ----")
    show_tasks(user_id, True)

    task_id = input("\nEnter task ID to delete (or press Enter to cancel): ").strip()
    if not task_id:
        print("Cancelled.")
        return

    try:
        task_id = int(task_id)
    except ValueError:
        print("Invalid ID!")
        return

    confirm = input(f"Are you sure you want to delete task #{task_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT name, description, status FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    task = cur.fetchone()

    if not task:
        print(f"Task #{task_id} not found!")
        conn.close()
        return

    name, desc, status = task

    cur.execute(
        """INSERT INTO history
        (task_id, user_id, name, description, status, change_type)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (task_id, user_id, name, desc, status, "deleted")
    )

    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()
    print(f"Task #{task_id} deleted successfully!")


def view_history(user_id):
    """View task history"""
    print("\n---- Task History ----")
    task_id = input("Enter task ID to view history (or press Enter to cancel): ").strip()

    if not task_id:
        print("Cancelled.")
        return

    try:
        task_id = int(task_id)
    except ValueError:
        print("Invalid ID!")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT name, description, status, changed_date, change_type
        FROM history
        WHERE task_id = ? AND user_id = ?
        ORDER BY changed_date
        """,
        (task_id, user_id)
    )
    history = cur.fetchall()
    conn.close()

    if not history:
        print(f"No history found for task #{task_id}!")
        return

    rows = []
    for i, entry in enumerate(history, start=1):
        name, desc, status, date, change = entry
        if desc and len(desc) > 20:
            desc = desc[:17] + "..."
        rows.append([i, name, desc if desc else "", status, date, change])

    print(f"\nHistory for Task #{task_id}:")
    headers = ["No.", "Name", "Description", "Status", "Date", "Change"]
    print_table(headers, rows)


# -------------------- Menus --------------------
def main_menu():
    """Show main menu"""
    print("\n" + "-" * 40)
    print("TASK MANAGER".center(40))
    print("-" * 40)
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    print("-" * 40)
    return input("Choose (1-3): ").strip()


def task_menu(username):
    """Show task menu"""
    print("\n" + "-" * 40)
    print(f"TASK MANAGER - {username}".center(40))
    print("-" * 40)
    print("1. Add Task")
    print("2. View Pending Tasks")
    print("3. View All Tasks")
    print("4. Edit Task")
    print("5. Complete Task")
    print("6. Delete Task")
    print("7. View Task History")
    print("8. Logout")
    print("9. Exit")
    print("-" * 40)
    return input("Choose (1-9): ").strip()


# -------------------- Main Program --------------------
def main():
    setup_database()

    logged_in_user_id = None
    logged_in_username = None

    while True:
        if logged_in_user_id is None:
            choice = main_menu()

            if choice == "1":
                register()
            elif choice == "2":
                logged_in_user_id, logged_in_username = login()
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice!")

        else:
            choice = task_menu(logged_in_username)

            if choice == "1":
                add_task(logged_in_user_id)
            elif choice == "2":
                show_tasks(logged_in_user_id, False)
            elif choice == "3":
                show_tasks(logged_in_user_id, True)
            elif choice == "4":
                edit_task(logged_in_user_id)
            elif choice == "5":
                complete_task(logged_in_user_id)
            elif choice == "6":
                delete_task(logged_in_user_id)
            elif choice == "7":
                view_history(logged_in_user_id)
            elif choice == "8":
                logged_in_user_id = None
                logged_in_username = None
                logout()
            elif choice == "9":
                print("Goodbye!")
                break
            else:
                print("Invalid choice!")


if __name__ == "__main__":
    main()