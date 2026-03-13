import sqlite3

subjects = {
    1: "Math II",
    2: "OOS",
    3: "CN",
    4: "GMM",
    5: "GTC"
}

subject_columns = {
    1: "mathII",
    2: "oos",
    3: "cn",
    4: "gmm",
    5: "gtc"
}

# Connecting to database
def connect_db():
    try:
        conn = sqlite3.connect("marks_management1.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                rollno INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                mathII INTEGER CHECK(mathII BETWEEN 0 AND 100),
                oos INTEGER CHECK(oos BETWEEN 0 AND 100),
                cn INTEGER CHECK(cn BETWEEN 0 AND 100),
                gmm INTEGER CHECK(gmm BETWEEN 0 AND 100),
                gtc INTEGER CHECK(gtc BETWEEN 0 AND 100)
            )
        ''')
        conn.commit()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        exit()

# Adding Students to Database 
def add_student(cursor, conn):
    try:
        name = input("Enter name: ").strip()
        while True:
            try:
                rollno = int(input("Enter rollno: "))
                cursor.execute("SELECT * FROM students WHERE rollno = ?", (rollno,))
                if cursor.fetchone():
                    print("Roll number already exists. Please enter a unique roll number.")
                else:
                    break
            except ValueError:
                print("Invalid input! Please enter a valid roll number.")
        
        marks = []
        for i in range(5):
            while True:
                try:
                    mark = int(input(f"Enter {subjects[i + 1]} marks (0-100): "))
                    if 0 <= mark <= 100:
                        marks.append(mark)
                        break
                    else:
                        print("Marks should be between 0 and 100.")
                except ValueError:
                    print("Invalid input! Please enter a valid number.")
                    
        cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", (rollno, name, *marks))
        conn.commit()
        print("Student added successfully...")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Deleting Students from Database
def delete_student(cursor, conn):
    try:
        roll_no = int(input("Enter rollno to delete: "))
        cursor.execute("SELECT * FROM students WHERE rollno = ?", (roll_no,))
        student = cursor.fetchone()
        if student:
            confirm = input(f"Are you sure you want to delete student {student[1]} (Roll No: {roll_no})? (yes/no): ").strip().lower()
            if confirm == "yes":
                cursor.execute("DELETE FROM students WHERE rollno = ?", (roll_no,))
                conn.commit()
                print("Student deleted successfully...")
            else:
                print("Deletion cancelled.")
        else:
            print("Student not found...")
    except ValueError:
        print("Invalid input! Please enter a valid roll number.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Updating Marks of students by Class Teacher (can update any subject)
def update_marks(cursor, conn):
    try:
        roll_no = int(input("Enter rollno to update: "))
        cursor.execute("SELECT * FROM students WHERE rollno = ?", (roll_no,))
        student = cursor.fetchone()
        if student:
            subject_id = int(input("Enter the subject ID (1-5): "))
            if 1 <= subject_id <= 5:
                new_marks = int(input(f"Enter new marks for {subjects[subject_id]} (0-100): "))
                if 0 <= new_marks <= 100:
                    column_name = subject_columns[subject_id]
                    cursor.execute(f"UPDATE students SET {column_name} = ? WHERE rollno = ?", (new_marks, roll_no))
                    conn.commit()
                    print("Marks updated successfully...")
                else:
                    print("Marks should be between 0 and 100.")
            else:
                print("Invalid subject ID...")
        else:
            print("Student not found...")
    except ValueError:
        print("Invalid input! Please enter numerical values only.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Update marks for a specific subject (Subject Teacher)
def update_subject_marks(cursor, conn, subject_id):
    try:
        print(f"\nUpdating marks for {subjects[subject_id]}")
        # First, show all students with their current marks for this subject
        display_students_for_subject(cursor, subject_id)
        
        roll_no = int(input("\nEnter rollno to update marks: "))
        column_name = subject_columns[subject_id]
        cursor.execute(f"SELECT rollno, name, {column_name} FROM students WHERE rollno = ?", (roll_no,))
        student = cursor.fetchone()
        
        if student:
            print(f"Current marks for {student[1]} (Roll No: {student[0]}) in {subjects[subject_id]}: {student[2]}")
            new_marks = int(input(f"Enter new marks for {subjects[subject_id]} (0-100): "))
            if 0 <= new_marks <= 100:
                cursor.execute(f"UPDATE students SET {column_name} = ? WHERE rollno = ?", (new_marks, roll_no))
                conn.commit()
                print("Marks updated successfully...")
            else:
                print("Marks should be between 0 and 100.")
        else:
            print("Student not found...")
    except ValueError:
        print("Invalid input! Please enter numerical values only.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Display Students according to required Order
def display_students(cursor, order_by="rollno ASC"):
    try:
        cursor.execute(f'''
            SELECT rollno, name, mathII, oos, cn, gmm, gtc, 
            (mathII + oos + cn + gmm + gtc) AS totalmarks 
            FROM students ORDER BY {order_by}
        ''')
        students = cursor.fetchall()
        if students:
            print("\n--- Student details ---")
            print("%-10s %-20s %-10s %-10s %-10s %-10s %-10s %-10s" % 
                  ("Rollno", "Name", "Math II", "OOS", "CN", "GMM", "GTC", "Total"))
            print("-" * 90)
            for st in students:
                print("%-10d %-20s %-10d %-10d %-10d %-10d %-10d %-10d" % st)
        else:
            print("No student records found.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Display Students for a specific subject
def display_students_for_subject(cursor, subject_id):
    try:
        column_name = subject_columns[subject_id]
        cursor.execute(f'''
            SELECT rollno, name, {column_name}
            FROM students ORDER BY rollno
        ''')
        students = cursor.fetchall()
        if students:
            print(f"\n--- Student details for {subjects[subject_id]} ---")
            print("%-10s %-20s %-10s" % ("Rollno", "Name", subjects[subject_id]))
            print("-" * 40)
            for st in students:
                print("%-10d %-20s %-10d" % st)
        else:
            print("No student records found.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")

# Menu System for Class Teacher
def class_teacher(cursor, conn):
    while True:
        try:
            print("\n==== Class Teacher Menu ====")
            print("1. Add student")
            print("2. Update marks for any subject")
            print("3. Delete student")
            print("4. View all students")
            print("0. Back to main menu")
            choice = int(input("Enter choice: "))
            if choice == 1:
                add_student(cursor, conn)
            elif choice == 2:
                update_marks(cursor, conn)
            elif choice == 3:
                delete_student(cursor, conn)
            elif choice == 4:
                display_students(cursor)
            elif choice == 0:
                break
            else:
                print("Invalid input. Please try again.")
        except ValueError:
            print("Invalid input! Please enter a number.")

# Menu System for Subject Teacher
def subject_teacher(cursor, conn):
    try:
        subject_id = 0
        while subject_id < 1 or subject_id > 5:
            try:
                subject_id = int(input("Enter your subject ID (1-5): "))
                if subject_id < 1 or subject_id > 5:
                    print("Invalid subject ID. Please enter a number between 1 and 5.")
            except ValueError:
                print("Invalid input! Please enter a number.")
        
        while True:
            try:
                print(f"\n==== {subjects[subject_id]} Teacher Menu ====")
                print(f"1. Update marks for {subjects[subject_id]}")
                print(f"2. View students with {subjects[subject_id]} marks")
                print("3. View all student details")
                print("0. Back to main menu")
                choice = int(input("Enter choice: "))
                if choice == 1:
                    update_subject_marks(cursor, conn, subject_id)
                elif choice == 2:
                    display_students_for_subject(cursor, subject_id)
                elif choice == 3:
                    display_students(cursor)
                elif choice == 0:
                    break
                else:
                    print("Invalid input. Please try again.")
            except ValueError:
                print("Invalid input! Please enter a number.")
    except Exception as e:
        print(f"Error: {e}")

# Show Marks of Students in Decreasing Order of Total Marks (Student View)
def student(cursor):
    print("\n==== Student Results (Ranked by Total Marks) ====")
    display_students(cursor, "totalmarks DESC")

# Main Menu of the Program
def main():
    conn, cursor = connect_db()
    try:
        while True:
            print("\n==== Student Marks Management System ====")
            print("1. Class Teacher")
            print("2. Subject Teacher")
            print("3. Student")
            print("0. Exit")
            try:
                choice = int(input("Enter choice: "))
                if choice == 1:
                    class_teacher(cursor, conn)
                elif choice == 2:
                    subject_teacher(cursor, conn)
                elif choice == 3:
                    student(cursor)
                elif choice == 0:
                    print("Exiting program...")
                    conn.close()
                    exit()
                else:
                    print("Invalid input. Please try again.")
            except ValueError:
                print("Invalid input! Please enter a number.")
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()