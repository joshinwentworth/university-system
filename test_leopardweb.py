import sqlite3
import pytest
from logic import Course, Student, Instructor, Admin
from main import login, student_menu, instructor_menu, admin_menu

# ==============================================================================
# LECTURE-ALIGNED TESTING STATE (Barry Boehm's Verification & Validation)
# Verification: "Are we building the product right?" (Program matches logic specifications)
# Validation: "Are we building the right product?" (System satisfies user workflows)
# ==============================================================================

@pytest.fixture
def db_conn():
    """
    TEST SETUP PHASE:
    Constructs an isolated, in-memory SQLite database instance populated with
    baseline seeded records to safely run test suites without modifying real files.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Recreate the exact database schema
    cursor.execute("""CREATE TABLE LOGIN (ID INTEGER PRIMARY KEY NOT NULL, EMAIL TEXT UNIQUE NOT NULL, PASSWORD TEXT NOT NULL, ROLE TEXT NOT NULL);""")
    cursor.execute("""CREATE TABLE ADMIN (ID INTEGER PRIMARY KEY NOT NULL, FIRST_NAME TEXT NOT NULL, LAST_NAME TEXT NOT NULL, TITLE TEXT NOT NULL, OFFICE TEXT NOT NULL, EMAIL TEXT NOT NULL, FOREIGN KEY(ID) REFERENCES LOGIN(ID));""")
    cursor.execute("""CREATE TABLE INSTRUCTOR (ID INTEGER PRIMARY KEY NOT NULL, FIRST_NAME TEXT NOT NULL, LAST_NAME TEXT NOT NULL, TITLE TEXT NOT NULL, HIREYEAR INTEGER NOT NULL, DEPT CHAR(4) NOT NULL, EMAIL TEXT NOT NULL, FOREIGN KEY(ID) REFERENCES LOGIN(ID));""")
    cursor.execute("""CREATE TABLE STUDENT (ID INTEGER PRIMARY KEY NOT NULL, FIRST_NAME TEXT NOT NULL, LAST_NAME TEXT NOT NULL, GRADYEAR INTEGER NOT NULL, MAJOR CHAR(4) NOT NULL, EMAIL TEXT NOT NULL, FOREIGN KEY(ID) REFERENCES LOGIN(ID));""")
    cursor.execute("""CREATE TABLE COURSE (CRN INTEGER PRIMARY KEY NOT NULL, TITLE TEXT NOT NULL, DEPARTMENT TEXT NOT NULL, TIME TEXT NOT NULL, DAYS TEXT NOT NULL, SEMESTER TEXT NOT NULL, YEAR INTEGER NOT NULL, CREDITS INTEGER NOT NULL, INSTRUCTOR_ID INTEGER, FOREIGN KEY(INSTRUCTOR_ID) REFERENCES INSTRUCTOR(ID));""")
    cursor.execute("""CREATE TABLE REGISTRATION (STUDENT_ID INTEGER NOT NULL, CRN INTEGER NOT NULL, PRIMARY KEY (STUDENT_ID, CRN), FOREIGN KEY(STUDENT_ID) REFERENCES STUDENT(ID), FOREIGN KEY(CRN) REFERENCES COURSE(CRN));""")
    
    # Populate testing baseline seed records
    cursor.execute("INSERT INTO LOGIN VALUES(1000, 'rubinv@wit.edu', 'pass123', 'Admin');")
    cursor.execute("INSERT INTO ADMIN VALUES(1000, 'Vera', 'Rubin', 'Registrar', 'Wentworth 101', 'rubinv@wit.edu');")
    
    cursor.execute("INSERT INTO LOGIN VALUES(2001, 'turinga@wit.edu', 'pass123', 'Instructor');")
    cursor.execute("INSERT INTO INSTRUCTOR VALUES(2001, 'Alan', 'Turing', 'Prof', 2010, 'BSCO', 'turinga@wit.edu');")
    
    cursor.execute("INSERT INTO LOGIN VALUES(3001, 'doej@student.wit.edu', 'pass123', 'Student');")
    cursor.execute("INSERT INTO STUDENT VALUES(3001, 'John', 'Doe', 2026, 'BSCO', 'doej@student.wit.edu');")
    
    cursor.execute("INSERT INTO COURSE VALUES(101, 'Intro to Programming', 'BSCO', '08:00', 'MWF', 'Fall', 2026, 4, 2001);")
    cursor.execute("INSERT INTO COURSE VALUES(102, 'Data Structures', 'BCOS', '10:00', 'TR', 'Fall', 2026, 4, 2002);")
    cursor.execute("INSERT INTO COURSE VALUES(103, 'Circuits I', 'BSEE', '08:00', 'MWF', 'Fall', 2026, 4, 2005);")
    
    conn.commit()
    yield conn
    conn.close()


# ==============================================================================
# FUNCTION 1: LOG-IN / LOG-OUT TESTS (All Users)
# ==============================================================================

# Case 1A: Admin Login Success (Typical)
def test_login_admin_success(db_conn, monkeypatch):
    # Setup
    inputs = iter(['rubinv@wit.edu', 'pass123'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    # Call
    user, role = login(db_conn)
    # Assertion
    assert role == 'Admin'
    assert user.first_name == 'Vera'

# Case 1B: Admin Login Failure - Incorrect Credentials (Abnormal/Unlikely)
def test_login_admin_wrong_password(db_conn, monkeypatch):
    # Setup
    inputs = iter(['rubinv@wit.edu', 'wrong_pass'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    # Call
    user, role = login(db_conn)
    # Assertion
    assert user is None
    assert role is None

# Case 1C: Student Login Verification (Typical)
def test_login_student_role(db_conn, monkeypatch):
    # Setup
    inputs = iter(['doej@student.wit.edu', 'pass123'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    # Call
    user, role = login(db_conn)
    # Assertion
    assert role == 'Student'

# Case 1D: Instructor Login Verification (Typical)
def test_login_instructor_role(db_conn, monkeypatch):
    # Setup
    inputs = iter(['turinga@wit.edu', 'pass123'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    # Call
    user, role = login(db_conn)
    # Assertion
    assert role == 'Instructor'

# Case 1E: Student Menu Logout (Typical)
def test_student_menu_logout(db_conn, monkeypatch, capsys):
    # Setup
    student = Student(db_conn, 3001, 'John', 'Doe', 'doej@student.wit.edu', 2026, 'BSCO')
    monkeypatch.setattr('builtins.input', lambda _: '6') # Selection '6' is logout in Student Menu
    # Call
    student_menu(student)
    # Assertion
    captured = capsys.readouterr()
    assert "Logging out..." in captured.out

# Case 1F: Instructor Menu Logout (Typical)
def test_instructor_menu_logout(db_conn, monkeypatch, capsys):
    # Setup
    instructor = Instructor(db_conn, 2001, 'Alan', 'Turing', 'turinga@wit.edu', 'Prof', 2010, 'BSCO')
    monkeypatch.setattr('builtins.input', lambda _: '6') # Selection '6' is logout in Instructor Menu
    # Call
    instructor_menu(instructor)
    # Assertion
    captured = capsys.readouterr()
    assert "Logging out..." in captured.out

# Case 1G: Admin Menu Logout (Typical)
def test_admin_menu_logout(db_conn, monkeypatch, capsys):
    # Setup
    admin = Admin(db_conn, 1000, 'Vera', 'Rubin', 'rubinv@wit.edu', 'Registrar', 'Wentworth 101')
    monkeypatch.setattr('builtins.input', lambda _: '8') # Selection '8' is logout in Admin Menu
    # Call
    admin_menu(admin)
    # Assertion
    captured = capsys.readouterr()
    assert "Logging out..." in captured.out


# ==============================================================================
# FUNCTION 2: SEARCH ALL COURSES (Default Search - All Users Required)
# ==============================================================================

# Case 2A: Default Search - Student Role (Typical)
def test_search_all_courses_as_student(db_conn):
    # Setup
    student = Student(db_conn, 3001, 'John', 'Doe', 'doej@student.wit.edu', 2026, 'BSCO')
    # Call
    all_courses = student.search_courses()
    # Assertion
    assert len(all_courses) >= 3

# Case 2B: Default Search - Instructor Role (Typical)
def test_search_all_courses_as_instructor(db_conn):
    # Setup
    instructor = Instructor(db_conn, 2001, 'Alan', 'Turing', 'turinga@wit.edu', 'Prof', 2010, 'BSCO')
    # Call
    all_courses = instructor.search_courses()
    # Assertion
    assert len(all_courses) >= 3

# Case 2C: Default Search - Admin Role (Typical)
def test_search_all_courses_as_admin(db_conn):
    # Setup
    admin = Admin(db_conn, 1000, 'Vera', 'Rubin', 'rubinv@wit.edu', 'Registrar', 'Wentworth 101')
    # Call
    all_courses = admin.search_courses()
    # Assertion
    assert len(all_courses) >= 3


# ==============================================================================
# FUNCTION 3: SEARCH COURSES BASED ON PARAMETERS (All Users Required)
# ==============================================================================

# Case 3A: Parameterized Lookup Match - Student Role (Typical)
def test_search_courses_by_parameter_student(db_conn):
    # Setup
    student = Student(db_conn, 3001, 'John', 'Doe', 'doej@student.wit.edu', 2026, 'BSCO')
    # Call
    parameter_courses = student.search_courses(param="Circuits")
    # Assertion
    assert len(parameter_courses) == 1
    assert parameter_courses[0].crn == 103

# Case 3B: Parameterized Lookup Match - Instructor Role (Typical)
def test_search_courses_by_parameter_instructor(db_conn):
    # Setup
    instructor = Instructor(db_conn, 2001, 'Alan', 'Turing', 'turinga@wit.edu', 'Prof', 2010, 'BSCO')
    # Call
    parameter_courses = instructor.search_courses(param="Intro")
    # Assertion
    assert len(parameter_courses) == 1
    assert parameter_courses[0].crn == 101

# Case 3C: Parameterized Lookup Match - Admin Role (Typical)
def test_search_courses_by_parameter_admin(db_conn):
    # Setup
    admin = Admin(db_conn, 1000, 'Vera', 'Rubin', 'rubinv@wit.edu', 'Registrar', 'Wentworth 101')
    # Call
    parameter_courses = admin.search_courses(param="Data Structures")
    # Assertion
    assert len(parameter_courses) == 1
    assert parameter_courses[0].crn == 102

# Case 3D: Parameterized Lookup No Match - Multiple Case Edge Coverage (Abnormal/Unlikely)
def test_search_courses_by_parameter_no_results(db_conn):
    # Setup
    student = Student(db_conn, 3001, 'John', 'Doe', 'doej@student.wit.edu', 2026, 'BSCO')
    # Call
    parameter_courses = student.search_courses(param="Art History")
    # Assertion
    assert len(parameter_courses) == 0


# ==============================================================================
# FUNCTION 4: ADD/REMOVE COURSE FROM SEMESTER SCHEDULE (Student)
# ==============================================================================

# Case 4A: Safe Registration Addition & Removal Sequence (Typical)
def test_student_add_and_remove_course_typical(db_conn):
    # Setup
    student = Student(db_conn, 3001, 'John', 'Doe', 'doej@student.wit.edu', 2026, 'BSCO')
    # Call & Assertion (Addition Segment)
    student.add_course(101)
    assert len(student._get_schedule()) == 1
    # Call & Assertion (Removal Segment)
    student.remove_course(101)
    assert len(student._get_schedule()) == 0

# Case 4B: Timetable Hour/Days Collision Check (Abnormal/Unlikely)
def test_student_add_course_conflict_unlikely(db_conn):
    # Setup
    student = Student(db_conn, 3001, 'John', 'Doe', 'doej@student.wit.edu', 2026, 'BSCO')
    # Call
    student.add_course(101) # Scheduled at 08:00 MWF
    student.add_course(103) # Overlaps exactly at 08:00 MWF
    # Assertion
    schedule = student._get_schedule()
    assert len(schedule) == 1
    assert schedule[0].crn == 101


# ==============================================================================
# FUNCTION 5: ASSEMBLE AND PRINT COURSE ROSTER (Instructor)
# ==============================================================================

# Case 5A: Roster Processing Containing Active Students (Typical)
def test_instructor_print_roster_populated(db_conn):
    # Setup
    instructor = Instructor(db_conn, 2001, 'Alan', 'Turing', 'turinga@wit.edu', 'Prof', 2010, 'BSCO')
    student = Student(db_conn, 3001, 'John', 'Doe', 'doej@student.wit.edu', 2026, 'BSCO')
    student.add_course(101) # Place student in instructor's class (CRN 101)
    # Call
    cursor = db_conn.cursor()
    cursor.execute("SELECT S.FIRST_NAME FROM STUDENT S JOIN REGISTRATION R ON S.ID = R.STUDENT_ID WHERE R.CRN = ? AND ? = 2001", (101, instructor.user_id))
    roster_data = cursor.fetchall()
    # Assertion
    assert len(roster_data) == 1
    assert roster_data[0][0] == 'John'

# Case 5B: Roster Processing Containing No Registrations (Abnormal/Typical Alternate)
def test_instructor_print_roster_empty(db_conn):
    # Setup
    instructor = Instructor(db_conn, 2001, 'Alan', 'Turing', 'turinga@wit.edu', 'Prof', 2010, 'BSCO')
    # Call
    cursor = db_conn.cursor()
    cursor.execute("SELECT S.FIRST_NAME FROM STUDENT S JOIN REGISTRATION R ON S.ID = R.STUDENT_ID WHERE R.CRN = 102")
    roster_data = cursor.fetchall()
    # Assertion
    assert len(roster_data) == 0


# ==============================================================================
# FUNCTION 6: ADD/REMOVE COURSES FROM THE SYSTEM (Admin)
# ==============================================================================

# Case 6A: Course System Insertion (Typical)
def test_admin_add_course_system(db_conn):
    # Setup
    admin = Admin(db_conn, 1000, 'Vera', 'Rubin', 'rubinv@wit.edu', 'Registrar', 'Wentworth 101')
    new_test_course = Course(201, 'Network Security', 'BSCO', '12:00', 'TR', 'Fall', 2026, 4, None)
    # Call
    admin.add_course(new_test_course)
    # Assertion
    cursor = db_conn.cursor()
    cursor.execute("SELECT TITLE FROM COURSE WHERE CRN = 201")
    added_course = cursor.fetchone()
    assert added_course is not None
    assert added_course[0] == 'Network Security'

# Case 6B: Course System Deletion (Typical Alternative)
def test_admin_remove_course_system(db_conn):
    # Setup
    admin = Admin(db_conn, 1000, 'Vera', 'Rubin', 'rubinv@wit.edu', 'Registrar', 'Wentworth 101')
    # Call
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM COURSE WHERE CRN = 101")
    db_conn.commit()
    # Assertion
    cursor.execute("SELECT * FROM COURSE WHERE CRN = 101")
    removed_course = cursor.fetchone()
    assert removed_course is None