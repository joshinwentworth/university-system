import sqlite3
import random

database = sqlite3.connect("LeopardWeb_Data.db") 

cursor = database.cursor() 

sql_command = """CREATE TABLE IF NOT EXISTS LOGIN (  
ID INTEGER PRIMARY KEY NOT NULL,
EMAIL TEXT UNIQUE NOT NULL,
PASSWORD TEXT NOT NULL,
ROLE TEXT NOT NULL)
;"""
cursor.execute(sql_command) 

sql_command = """CREATE TABLE IF NOT EXISTS ADMIN (  
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
TITLE TEXT NOT NULL,
OFFICE TEXT NOT NULL,
EMAIL TEXT NOT NULL,
FOREIGN KEY(ID) REFERENCES LOGIN(ID))
;"""
cursor.execute(sql_command) 

sql_command = """CREATE TABLE IF NOT EXISTS INSTRUCTOR (  
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
TITLE TEXT NOT NULL,
HIREYEAR INTEGER NOT NULL,
DEPT CHAR(4) NOT NULL,
EMAIL TEXT NOT NULL,
FOREIGN KEY(ID) REFERENCES LOGIN(ID))
;"""
cursor.execute(sql_command) 

sql_command = """CREATE TABLE IF NOT EXISTS STUDENT (  
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
GRADYEAR INTEGER NOT NULL,
MAJOR CHAR(4) NOT NULL,
EMAIL TEXT NOT NULL,
FOREIGN KEY(ID) REFERENCES LOGIN(ID))
;"""
cursor.execute(sql_command) 

sql_command = """CREATE TABLE IF NOT EXISTS COURSE (  
CRN INTEGER PRIMARY KEY NOT NULL,
TITLE TEXT NOT NULL,
DEPARTMENT TEXT NOT NULL,
TIME TEXT NOT NULL,
DAYS TEXT NOT NULL,
SEMESTER TEXT NOT NULL,
YEAR INTEGER NOT NULL,
CREDITS INTEGER NOT NULL,
INSTRUCTOR_ID INTEGER,
FOREIGN KEY(INSTRUCTOR_ID) REFERENCES INSTRUCTOR(ID))
;"""
cursor.execute(sql_command) 

sql_command = """CREATE TABLE IF NOT EXISTS REGISTRATION (  
STUDENT_ID INTEGER NOT NULL,
CRN INTEGER NOT NULL,
PRIMARY KEY (STUDENT_ID, CRN),
FOREIGN KEY(STUDENT_ID) REFERENCES STUDENT(ID),
FOREIGN KEY(CRN) REFERENCES COURSE(CRN))
;"""
cursor.execute(sql_command) 


admins = [
    (1000, 'Mark', 'Thompson', 'President', 'WIT', 'thompsonm@wit.edu'),
    (1001, 'Ali', 'Khabari', 'Dean', 'School of Engineering', 'khabaria@wit.edu'),
    (1002, 'Afsaneh', 'Ghanavati', 'Director', 'BSCO', 'ghanavatia@wit.edu')
]
for admin_info in admins:
    password = f"{admin_info[1][0].upper()}{admin_info[2][0].upper()}admin26!"
    cursor.execute(f"INSERT OR IGNORE INTO LOGIN VALUES({admin_info[0]}, '{admin_info[5]}', '{password}', 'Admin');")
    cursor.execute(f"INSERT OR IGNORE INTO ADMIN VALUES({admin_info[0]}, '{admin_info[1]}', '{admin_info[2]}', '{admin_info[3]}', '{admin_info[4]}', '{admin_info[5]}');")


instructors = [
    ("Hayden", "Pierce"), ("Joey", "Cotta"), ("Jack", "Newton"), 
    ("Mark", "Murphy"), ("Matt", "Murphy"), ("Jon", "Savage"),
    ("Dylan", "Brilliant"), ("Teddy", "Doyle"), ("Nate", "Lowe"), 
    ("Nate", "Bergquistguimond"), ("Ezra", "Blasko"), ("Everett", "Miller"),
    ("Ryan", "Ballard"), ("Evan", "McIntire"), ("Jacob", "Thomas")
]
instructor_depts = ['BSCO', 'BSCO', 'BSEE', 'BSEE', 'COMP', 'COMP', 'ARCH', 'ARCH', 'CONM', 'CONM', 'MATH', 'MATH', 'PHYS', 'ENGL', 'ENGL']
instructor_titles = ['Assistant Professor', 'Associate Professor', 'Professor']
for user_id, (first_name, last_name) in enumerate(instructors, start=2000):
    dept = instructor_depts[user_id - 2000]
    title = random.choice(instructor_titles)
    hire_year = random.randint(1950, 2026)
    base_prefix = f"{last_name.lower()}{first_name[0].lower()}"
    email = f"{base_prefix}@wit.edu"
    counter = 1
    while True:
        cursor.execute("SELECT EMAIL FROM LOGIN WHERE EMAIL = ?", (email,))
        if not cursor.fetchone():
            break
        email = f"{base_prefix}{counter}@wit.edu"
        counter += 1
    options = ["#", "!", "$"]
    symbol = random.choice(options)
    password = f"{first_name[0].upper()}{last_name[0].upper()}{dept.lower()}{hire_year%100}{symbol}"
    cursor.execute(f"INSERT OR IGNORE INTO LOGIN VALUES({user_id}, '{email}', '{password}', 'Instructor');")
    cursor.execute(f"INSERT OR IGNORE INTO INSTRUCTOR VALUES({user_id}, '{first_name}', '{last_name}', '{title}', {hire_year}, '{dept}', '{email}');")


students = [
    ("Arman", "Kazemi"), ("Ashton", "Vallejo"), ("Beshoy", "Gawargi"), ("David", "Vozzo"),
    ("Harrison", "Brown"), ("Joe", "Machado"), ("Joshua", "Kolasa"), ("Milo", "Silverman"),
    ("Rafael", "Enamorado"), ("Sreynith", "Ny"), ("Waldy", "JeanCharles"), ("Waylon", "MacNeil"),
    ("Christopher", "Hurst"), ("Henry", "Brown"), ("Josiah", "Hughes"), ("Kaleigh", "West"),
    ("Lily", "Pattison"), ("Michael", "Sibert"), ("Robert", "Papazian"), ("Dillon", "Borowski")
]
majors = ["BSCO", "BSEE", "COMP", "ARCH", "CONM"] * 4
for user_id, (first_name, last_name) in enumerate(students, start=3000):
    major = majors[user_id - 3000]
    gradyear = random.randint(2026, 2030)
    base_prefix = f"{last_name.lower()}{first_name[0].lower()}"
    email = f"{base_prefix}@wit.edu"
    counter = 1
    while True:
        cursor.execute("SELECT EMAIL FROM LOGIN WHERE EMAIL = ?", (email,))
        if not cursor.fetchone():
            break
        email = f"{base_prefix}{counter}@wit.edu"
        counter += 1
    options = ["#", "!", "$"]
    symbol = random.choice(options)
    password = f"{first_name[0].upper()}{last_name[0].upper()}{major.lower()}{gradyear%100}{symbol}"
    cursor.execute(f"INSERT OR IGNORE INTO LOGIN VALUES({user_id}, '{email}', '{password}', 'Student');")
    cursor.execute(f"INSERT OR IGNORE INTO STUDENT VALUES({user_id}, '{first_name}', '{last_name}', {gradyear}, '{major}', '{email}');")


base_courses = [
    # BSCO
    (0, "Digital Logic", "BSCO", "08", "MW", 4, 2000),
    (1, "Computer Architecture", "BSCO", "10", "TR", 4, 2001),
    (2, "Applied Programming Concepts", "BSCO", "13", "MW", 4, 2000),
    
    # BSEE
    (3, "Object Oriented Programming", "BSEE", "08", "MW", 4, 2002),
    (4, "Signals & Systems", "BSEE", "10", "TR", 4, 2003),
    (5, "Microcontrollers Using C Programming", "BSEE", "13", "MW", 4, 2002),
    
    # COMP
    (6, "Computer Science I", "COMP", "08", "MW", 4, 2004),
    (7, "Discrete Math", "COMP", "10", "TR", 4, 2005),
    (8, "Algorithms", "COMP", "13", "MW", 4, 2004),
    
    # ARCH
    (9, "Architectural Design Studio I", "ARCH", "08", "MW", 4, 2006),
    (10, "History of Architecture", "ARCH", "10", "TR", 4, 2007),
    (11, "Building Materials", "ARCH", "13", "MW", 4, 2006),
    
    # CONM
    (12, "Intro to Construction Management", "CONM", "08", "MW", 4, 2008),
    (13, "Construction Leadership", "CONM", "10", "TR", 4, 2009),
    (14, "Construction Safety", "CONM", "13", "MW", 4, 2008),
    
    # General Education
    (15, "Calculus I", "MATH", "12", "MTWR", 4, 2010),
    (16, "Physics I", "PHYS", "08", "TR", 4, 2012),
    (17, "English I", "ENGL", "14", "TR", 4, 2013),
    (18, "Calculus II", "MATH", "10", "MW", 4, 2011),
    (19, "Physics II", "PHYS", "13", "TR", 4, 2012)
]
semesters = [("Summer", 2026, 100), ("Fall", 2026, 200), ("Spring", 2027, 300)]
courses = []
for sem_name, sem_year, offset in semesters:
    for c in base_courses:
        courses.append((c[0] + offset, c[1], c[2], c[3], c[4], sem_name, sem_year, c[5], c[6]))
for course_info in courses:
    cursor.execute(f"INSERT OR IGNORE INTO COURSE VALUES({course_info[0]}, '{course_info[1]}', '{course_info[2]}', '{course_info[3]}', '{course_info[4]}', '{course_info[5]}', {course_info[6]}, {course_info[7]}, {course_info[8]});")


print("Entire table")
cursor.execute("""SELECT * FROM COURSE""")
query_result = cursor.fetchall()
  
for i in query_result:
	print(i)

database.commit() 
database.close()