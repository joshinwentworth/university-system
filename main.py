import sqlite3
from logic import Student, Instructor, Admin, Course

def login(conn):
    cursor = conn.cursor()
    print("Welcome to LeopardWeb Registration System!")
    email = input("Email: ")
    password = input("Password: ")

    cursor.execute("SELECT ID, ROLE FROM LOGIN WHERE EMAIL = ? AND PASSWORD = ?", (email, password))
    user_data = cursor.fetchone()

    if not user_data:
        print("Invalid credentials.")
        return None, None

    user_id, role = user_data

    if role == 'Student':
        cursor.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL, GRADYEAR, MAJOR FROM STUDENT WHERE ID = ?", (user_id,))
        data = cursor.fetchone()
        return Student(conn, user_id, data[0], data[1], data[2], data[3], data[4]), role
    elif role == 'Instructor':
        cursor.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL, TITLE, HIREYEAR, DEPT FROM INSTRUCTOR WHERE ID = ?", (user_id,))
        data = cursor.fetchone()
        return Instructor(conn, user_id, data[0], data[1], data[2], data[3], data[4], data[5]), role
    elif role == 'Admin':
        cursor.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL, TITLE, OFFICE FROM ADMIN WHERE ID = ?", (user_id,))
        data = cursor.fetchone()
        return Admin(conn, user_id, data[0], data[1], data[2], data[3], data[4]), role

def student_menu(user):
    while True:
        print(f"\nStudent Menu: Hello {user.first_name} {user.last_name}...")
        print("1. Search all courses")
        print("2. Search courses by parameters")
        print("3. Add course to schedule")
        print("4. Remove course from schedule")
        print("5. Print schedule")
        print("6. Logout")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            user.search_courses()
        elif choice == '2':
            param = input("Enter search keyword (Title or Dept): ")
            user.search_courses(param)
        elif choice == '3':
            crn = int(input("Enter CRN to add: "))
            user.add_course(crn)
        elif choice == '4':
            crn = int(input("Enter CRN to remove: "))
            user.remove_course(crn)
        elif choice == '5':
            user.print_schedule()
        elif choice == '6':
            print("Logging out...")
            break

def instructor_menu(user):
    while True:
        print(f"\nInstructor Menu: Hello {user.first_name} {user.last_name}...")
        print("1. Search all courses")
        print("2. Search courses by parameters")
        print("3. Print teaching schedule")
        print("4. Search course roster for specific student")
        print("5. Print general course roster")
        print("6. Logout")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            user.search_courses()
        elif choice == '2':
            param = input("Enter search keyword (Title or Dept): ")
            user.search_courses(param)
        elif choice == '3':
            user.print_teaching_schedule()
        elif choice == '4':
            crn = int(input("Enter CRN to search within: "))
            search_keyword = input("Enter student's first or last name to search: ")
            user.search_roster(crn, search_keyword)
        elif choice == '5':
            crn = int(input("Enter CRN to view entire roster: "))
            user.print_roster(crn)
        elif choice == '6':
            print("Logging out...")
            break

def admin_menu(user):
    while True:
        print(f"\nAdmin Menu: Hello {user.first_name} {user.last_name}...")
        print("1. Search all courses")
        print("2. Search courses by parameters")
        print("3. Print course roster")
        print("4. Add new course")
        print("5. Link/Unlink instructor to course")
        print("6. Add/Remove student from course")
        print("7. Add new user (Student/Instructor) to system")
        print("8. Logout")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            user.search_courses()
        elif choice == '2':
            param = input("Enter search keyword (Title or Dept): ")
            user.search_courses(param)
        elif choice == '3':
            crn = int(input("Enter CRN to view roster: "))
            user.print_roster(crn)
        elif choice == '4':
            crn = int(input("CRN: "))
            title = input("Title: ")
            dept = input("Department: ")
            time = input("Time (e.g., 14:00): ")
            days = input("Days (e.g., MWF): ")
            sem = input("Semester: ")
            year = int(input("Year: "))
            cred = int(input("Credits: "))
            inst_input = input("Instructor ID (or leave blank): ")
            inst_id = int(inst_input) if inst_input.strip() else None
            
            new_course = Course(crn, title, dept, time, days, sem, year, cred, inst_id)
            user.add_course(new_course)
        elif choice == '5':
            crn = int(input("Enter CRN: "))
            inst_input = input("Enter new Instructor ID (leave blank to unlink): ")
            inst_id = int(inst_input) if inst_input.strip() else None
            user.link_instructor(crn, inst_id)
        elif choice == '6':
            action = input("Type 'add' or 'remove': ").lower()
            if action in ['add', 'remove']:
                student_id = int(input("Student ID: "))
                crn = int(input("CRN: "))
                user.manage_student_enrollment(student_id, crn, action)
        elif choice == '7':
            print("\n--- Add New User ---")
            role = input("Role (Student/Instructor): ").capitalize()
            if role in ['Student', 'Instructor']:
                first_name = input("First Name: ")
                last_name = input("Last Name: ")
                email = input("Email: ")
                password = input("Password: ")
                
                if role == 'Student':
                    grad_year = int(input("Expected Graduation Year: "))
                    major = input("Major (e.g., BSCO): ")
                    user.add_user(role, first_name, last_name, email, password, grad_year=grad_year, major=major)
                elif role == 'Instructor':
                    title = input("Title (e.g., Prof, Assistant Prof): ")
                    hire_year = int(input("Hire Year: "))
                    dept = input("Department (e.g., BCOS): ")
                    user.add_user(role, first_name, last_name, email, password, title=title, hire_year=hire_year, dept=dept)
            else:
                print("Invalid role selected. Must be 'Student' or 'Instructor'.")
        elif choice == '8':
            print("Logging out...")
            break

def main():
    conn = sqlite3.connect("LeopardWeb_Data.db")
    
    while True:
        user_obj, role = login(conn)
        if user_obj:
            if role == 'Student':
                student_menu(user_obj)
            elif role == 'Instructor':
                instructor_menu(user_obj)
            elif role == 'Admin':
                admin_menu(user_obj)
        
        cont = input("\nNew login? (y/n): ").lower()
        if cont != 'y':
            break

    conn.close()
    print("Exiting LeopardWeb. Thank you for using our program.")

if __name__ == "__main__":
    main()