import sqlite3

# ---------- Database Setup ----------
def initialize_database():
    conn = sqlite3.connect("marks_management.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        rollno INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        marks1 INTEGER,
        marks2 INTEGER,
        marks3 INTEGER,
        marks4 INTEGER,
        marks5 INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    return conn, cursor


# ---------- Add Student ----------
def add_new_student(cur, conn):

    name = input("Enter student name: ")

    while True:
        try:
            roll = int(input("Enter roll number: "))
            cur.execute("SELECT rollno FROM students WHERE rollno=?", (roll,))
            if cur.fetchone():
                print("Roll number already exists.")
            else:
                break
        except:
            print("Invalid roll number.")

    marks = []

    for i in range(1,6):
        while True:
            try:
                m = int(input(f"Enter marks for subject {i} (0-100): "))
                if 0 <= m <= 100:
                    marks.append(m)
                    break
                else:
                    print("Marks must be between 0 and 100.")
            except:
                print("Invalid input.")

    cur.execute(
        "INSERT INTO students (rollno,name,marks1,marks2,marks3,marks4,marks5) VALUES (?,?,?,?,?,?,?)",
        (roll,name,*marks)
    )

    conn.commit()
    print("Student added successfully.")


# ---------- Delete Student ----------
def delete_student(cur, conn):

    try:
        roll = int(input("Enter roll number to delete: "))
        cur.execute("SELECT name FROM students WHERE rollno=?", (roll,))
        record = cur.fetchone()

        if record:
            confirm = input(f"Delete record of {record[0]}? (yes/no): ")

            if confirm.lower() == "yes":
                cur.execute("DELETE FROM students WHERE rollno=?", (roll,))
                conn.commit()
                print("Record deleted.")
        else:
            print("Student not found.")

    except:
        print("Invalid input.")


# ---------- Update Marks ----------
def update_marks(cur, conn):

    try:
        roll = int(input("Enter roll number: "))
        cur.execute("SELECT * FROM students WHERE rollno=?", (roll,))
        record = cur.fetchone()

        if not record:
            print("Student not found.")
            return

        subject = int(input("Enter subject number (1-5): "))
        new_marks = int(input("Enter new marks: "))

        if 1 <= subject <= 5 and 0 <= new_marks <= 100:

            query = f"UPDATE students SET marks{subject}=? WHERE rollno=?"
            cur.execute(query,(new_marks,roll))

            conn.commit()
            print("Marks updated successfully.")

        else:
            print("Invalid subject or marks.")

    except:
        print("Invalid input.")


# ---------- Search Student ----------
def search_student(cur):

    try:
        roll = int(input("Enter roll number to search: "))

        cur.execute("SELECT * FROM students WHERE rollno=?", (roll,))
        record = cur.fetchone()

        if record:
            print("\nStudent Found")
            print("Roll No:",record[0])
            print("Name:",record[1])
            print("Marks:",record[2:7])
            print("Created At:",record[7])
        else:
            print("Student not found.")

    except:
        print("Invalid input.")


# ---------- Display Students ----------
def display_students(cur, order="rollno ASC"):

    cur.execute(f"""
        SELECT rollno,name,marks1,marks2,marks3,marks4,marks5,
        (marks1+marks2+marks3+marks4+marks5) AS total,
        ROUND((marks1+marks2+marks3+marks4+marks5)/5.0,2) AS avg
        FROM students
        ORDER BY {order}
    """)

    rows = cur.fetchall()

    if not rows:
        print("No records found.")
        return

    print("\n--- Student details ---")
    print("RollNo   Name                 S1  S2  S3  S4  S5  Total Avg")
    print("-"*65)

    for r in rows:
        print("%-8d %-20s %-3d %-3d %-3d %-3d %-3d %-4d %-5.2f" % r)


# ---------- Subject Teacher ----------
def subject_teacher_menu(cur, conn):

    try:
        sub = int(input("Enter subject number (1-5): "))

        if sub < 1 or sub > 5:
            print("Invalid subject.")
            return

        while True:

            print(f"\n==== Subject {sub} Teacher Menu ====")
            print("1 Update Marks")
            print("2 View Subject Marks")
            print("0 Back")

            choice = int(input("Choice: "))

            if choice == 1:

                roll = int(input("Enter roll number: "))
                marks = int(input("Enter new marks: "))

                if 0 <= marks <= 100:

                    cur.execute(
                        f"UPDATE students SET marks{sub}=? WHERE rollno=?",
                        (marks,roll)
                    )

                    conn.commit()
                    print("Marks updated.")

            elif choice == 2:

                cur.execute(f"SELECT rollno,name,marks{sub} FROM students")
                data = cur.fetchall()

                print(f"\n--- Student details for Subject {sub} ---")
                print("RollNo   Name                 Marks")
                print("-"*40)

                for d in data:
                    print("%-8d %-20s %-3d" % d)

            elif choice == 0:
                break

    except:
        print("Invalid input.")


# ---------- Class Teacher ----------
def class_teacher_menu(cur, conn):

    while True:

        print("\n==== Class Teacher Menu ====")
        print("1 Add Student")
        print("2 Update Marks")
        print("3 Delete Student")
        print("4 Display Students")
        print("5 Search Student")
        print("0 Back")

        try:
            choice = int(input("Choice: "))

            if choice == 1:
                add_new_student(cur,conn)

            elif choice == 2:
                update_marks(cur,conn)

            elif choice == 3:
                delete_student(cur,conn)

            elif choice == 4:
                display_students(cur)

            elif choice == 5:
                search_student(cur)

            elif choice == 0:
                break

        except:
            print("Invalid choice.")


# ---------- Student View ----------
def student_view(cur):

    print("\n==== Student Marks Management System ====")
    print("\n--- Rank List ---")
    display_students(cur,"total DESC")


# ---------- Main Program ----------
def main():

    conn,cur = initialize_database()

    while True:

        print("\n==== Student Marks Management System ====")
        print("1 Class Teacher")
        print("2 Subject Teacher")
        print("3 Student")
        print("0 Exit")

        try:
            option = int(input("Enter choice: "))

            if option == 1:
                class_teacher_menu(cur,conn)

            elif option == 2:
                subject_teacher_menu(cur,conn)

            elif option == 3:
                student_view(cur)

            elif option == 0:
                print("Program closed.")
                conn.close()
                break

        except:
            print("Invalid input.")


if __name__ == "__main__":
    main()