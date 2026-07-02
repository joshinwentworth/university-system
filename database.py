import sqlite3

# database file connection 
database = sqlite3.connect("LeopardWeb_Data.db") 
  
# cursor objects are used to traverse, search, grab, etc. information from the database, similar to indices or pointers  
cursor = database.cursor() 
  
# SQL command to create a table in the database 
sql_command = """CREATE TABLE IF NOT EXISTS LOGIN (  
ID INTEGER PRIMARY KEY NOT NULL,
EMAIL TEXT UNIQUE NOT NULL,
PASSWORD TEXT NOT NULL,
ROLE TEXT NOT NULL)
;"""
  
# execute the statement 
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
  
# SQL command to insert the data in the table, must be done one at a time 
sql_command = """INSERT OR IGNORE INTO LOGIN VALUES(1000, 'rubinv@wit.edu', 'pass123', 'Admin');"""
cursor.execute(sql_command) 

sql_command = """INSERT OR IGNORE INTO ADMIN VALUES(1000, 'Vera', 'Rubin', 'Registrar', 'Wentworth 101', 'rubinv@wit.edu');"""
cursor.execute(sql_command) 

# POPULATING THE REST OF THE REQUIRED SEED DATA VIA LOOPS
instructors = [
    ("Alan", "Turing", "Prof", 2010, "BSCO"), ("Grace", "Hopper", "Prof", 2005, "BCOS"),
    ("Ada", "Lovelace", "Prof", 2012, "BSCO"), ("John", "Von Neumann", "Prof", 2008, "BCOS"),
    ("Nikola", "Tesla", "Prof", 2015, "BSEE"), ("Thomas", "Edison", "Prof", 2011, "BSEE"),
    ("Marie", "Curie", "Prof", 2009, "BSAS"), ("Isaac", "Newton", "Prof", 2001, "BSAS"),
    ("Albert", "Einstein", "Prof", 2004, "BSAS"), ("Galileo", "Galilei", "Prof", 2007, "BSAS"),
    ("Katie", "Bouman", "Prof", 2019, "BCOS"), ("Margaret", "Hamilton", "Prof", 2016, "BSCO"),
    ("Tim", "Berners-Lee", "Prof", 2014, "BSCO"), ("Linus", "Torvalds", "Prof", 2018, "BCOS"),
    ("Donald", "Knuth", "Prof", 2006, "BSCO")
]
for user_id, (first_name, last_name, title, hire_year, dept) in enumerate(instructors, start=2001):
    email = f"{last_name.lower()}{first_name[0].lower()}@wit.edu"
    cursor.execute(f"INSERT OR IGNORE INTO LOGIN VALUES({user_id}, '{email}', 'pass123', 'Instructor');")
    cursor.execute(f"INSERT OR IGNORE INTO INSTRUCTOR VALUES({user_id}, '{first_name}', '{last_name}', '{title}', {hire_year}, '{dept}', '{email}');")

students = [
    ("John", "Doe"), ("Jane", "Smith"), ("Alice", "Johnson"), ("Bob", "Williams"),
    ("Charlie", "Brown"), ("Diana", "Prince"), ("Evan", "Wright"), ("Fiona", "Gallagher"),
    ("George", "Miller"), ("Hannah", "Davis"), ("Ian", "Moore"), ("Julia", "Taylor"),
    ("Kevin", "Anderson"), ("Laura", "Thomas"), ("Michael", "Jackson"), ("Nina", "White"),
    ("Oscar", "Harris"), ("Paula", "Martin"), ("Quinn", "Thompson"), ("Rachel", "Garcia")
]
for user_id, (first_name, last_name) in enumerate(students, start=3001):
    email = f"{last_name.lower()}{first_name[0].lower()}@student.wit.edu"
    cursor.execute(f"INSERT OR IGNORE INTO LOGIN VALUES({user_id}, '{email}', 'pass123', 'Student');")
    cursor.execute(f"INSERT OR IGNORE INTO STUDENT VALUES({user_id}, '{first_name}', '{last_name}', 2026, 'BSCO', '{email}');")

courses = [
    (101, "Intro to Programming", "BSCO", "08:00", "MWF", "Fall", 2026, 4, 2001),
    (102, "Data Structures", "BCOS", "10:00", "TR", "Fall", 2026, 4, 2002),
    (103, "Circuits I", "BSEE", "13:00", "MWF", "Fall", 2026, 4, 2005),
    (104, "Calculus I", "BSAS", "09:00", "MWF", "Fall", 2026, 4, 2008),
    (105, "Physics I", "BSAS", "11:00", "TR", "Fall", 2026, 4, 2007),
    (106, "Computer Networks", "BSCO", "14:00", "MW", "Fall", 2026, 4, 2003),
    (107, "Operating Systems", "BCOS", "15:00", "TR", "Fall", 2026, 4, 2004),
    (108, "Digital Logic", "BSEE", "10:00", "MWF", "Fall", 2026, 4, 2006),
    (109, "Linear Algebra", "BSAS", "12:00", "TR", "Fall", 2026, 4, 2009),
    (110, "Thermodynamics", "BSAS", "08:00", "TR", "Fall", 2026, 4, 2010),
    (111, "Software Engineering", "BCOS", "13:00", "MW", "Fall", 2026, 4, 2011),
    (112, "Embedded Systems", "BSCO", "09:00", "TR", "Fall", 2026, 4, 2012),
    (113, "Web Development", "BSCO", "16:00", "MW", "Fall", 2026, 3, 2013),
    (114, "Machine Learning", "BCOS", "14:00", "TR", "Fall", 2026, 4, 2014),
    (115, "Algorithms", "BSCO", "11:00", "MWF", "Fall", 2026, 4, 2015),
    (116, "Electromagnetics", "BSEE", "15:00", "MWF", "Fall", 2026, 4, 2005),
    (117, "Differential Equations", "BSAS", "10:00", "MWF", "Fall", 2026, 4, 2008),
    (118, "Chemistry I", "BSAS", "13:00", "TR", "Fall", 2026, 4, 2007),
    (119, "Ethics in Tech", "BSCO", "16:00", "TR", "Fall", 2026, 3, 2001),
    (120, "Senior Project", "BCOS", "12:00", "F", "Fall", 2026, 4, 2002)
]
for course_info in courses:
    cursor.execute(f"INSERT OR IGNORE INTO COURSE VALUES({course_info[0]}, '{course_info[1]}', '{course_info[2]}', '{course_info[3]}', '{course_info[4]}', '{course_info[5]}', {course_info[6]}, {course_info[7]}, {course_info[8]});")

# QUERY FOR ALL 
print("Entire table")
cursor.execute("""SELECT * FROM COURSE""")
query_result = cursor.fetchall()
  
for i in query_result:
	print(i)

# To save the changes in the files. Never skip this.  
# If we skip this, nothing will be saved in the database. 
database.commit() 
  
# close the connection 
database.close()