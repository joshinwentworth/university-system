import sqlite3

# database file connection 
database = sqlite3.connect(r"C:\Users\hayde\Desktop\ELEC3225 A3\assignment3.db")
  
# cursor objects are used to traverse, search, grab, etc. information from the database, similar to indices or pointers  
cursor = database.cursor() 
  
# SQL command to create a table in the database 
sql_command = """CREATE TABLE IF NOT EXISTS COURSE (   
CRN INTEGER PRIMARY KEY NOT NULL, 
TITLE TEXT NOT NULL, 
DEPARTMENT TEXT NOT NULL, 
TIME TEXT NOT NULL, 
DAY TEXT NOT NULL, 
SEMESTER TEXT NOT NULL, 
YEAR INTEGER NOT NULL, 
CREDITS INTEGER NOT NULL) 
;"""

# execute the statement 
cursor.execute(sql_command) 

# SQL command to insert the data in the table 
sql_command = """INSERT INTO COURSE VALUES(1001, 'History 101', 'HUSS', '1:00 PM', 'M,W', 'Fall', 2001, 4);""" 
cursor.execute(sql_command)

# SQL command to insert the data in the table 
sql_command = """INSERT INTO COURSE VALUES(1002, 'Math 101', 'BSAS', '8:00 AM', 'M,Tu,W', 'Spring', 2001, 4);""" 
cursor.execute(sql_command)

# SQL command to insert the data in the table 
sql_command = """INSERT INTO COURSE VALUES(1003, 'Science 101', 'BSCO', '9:00 AM', 'W,Th,F', 'Fall', 2004, 3);""" 
cursor.execute(sql_command)

# SQL command to insert the data in the table 
sql_command = """INSERT INTO COURSE VALUES(1004, 'Literature 101', 'BCOS', '10:00 AM', 'M,Th', 'Fall', 2011, 4);""" 
cursor.execute(sql_command)

# SQL command to insert the data in the table
sql_command = """INSERT INTO COURSE VALUES(1005, 'Biology 101', 'BSME', '12:00 PM', 'Th,F', 'Summer', 2005, 4);""" 
cursor.execute(sql_command)

# Updates
# Add 2 students
cursor.execute("INSERT OR IGNORE INTO STUDENT VALUES(10011, 'John', 'Doe', 2027, 'BSCO', 'doej@wit.edu');")
cursor.execute("INSERT OR IGNORE INTO STUDENT VALUES(10012, 'Jane', 'Doe', 2028, 'BSEE', 'doej1@wit.edu');")

# Remove 1 instructor (Joseph Fourier)
cursor.execute("DELETE FROM INSTRUCTOR WHERE ID = '20001';")

# Update 1 administrator (Vera Rubin's title to "Vice-President")
cursor.execute("UPDATE ADMIN SET TITLE = 'Vice-President' WHERE ID = '30002';")

# QUERY FOR ALL
print("Entire STUDENT table")
cursor.execute("""SELECT * FROM STUDENT""")
query_result = cursor.fetchall()

for i in query_result:
	print(i)

print("\nEntire INSTRUCTOR table")
cursor.execute("""SELECT * FROM INSTRUCTOR""")
query_result = cursor.fetchall()

for i in query_result:
	print(i)

print("\nEntire ADMIN table")
cursor.execute("""SELECT * FROM ADMIN""")
query_result = cursor.fetchall()

for i in query_result:
	print(i)

print("\nEntire COURSE table")
cursor.execute("""SELECT * FROM COURSE""")
query_result = cursor.fetchall()

for i in query_result:
	print(i)

# QUERY FOR SOME
print("\nInstructors matched to courses via department")
cursor.execute("""SELECT COURSE.CRN, COURSE.TITLE, COURSE.DEPARTMENT, INSTRUCTOR.NAME, INSTRUCTOR.SURNAME 
                  FROM COURSE 
                  INNER JOIN INSTRUCTOR ON COURSE.DEPARTMENT = INSTRUCTOR.DEPT""")
query_result = cursor.fetchall()

for i in query_result:
	print(f"Course: {i[0]} - {i[1]} [{i[2]}] | Instructor: Prof. {i[3]} {i[4]}")

cursor.execute("SELECT CRN, TITLE, DEPARTMENT FROM COURSE;")
all_courses = cursor.fetchall()

for course in all_courses:
    print("\nCourse ID:", course[0], "| Title:", course[1], "| Department:", course[2])
    
    cursor.execute("SELECT ID, NAME, SURNAME FROM INSTRUCTOR WHERE DEPT = '" + course[2] + "';")
    matching_instructors = cursor.fetchall()
    
    if len(matching_instructors) == 0:
        print("\tFlag: No matching instructors found for this department.")
    else:
        for instructor in matching_instructors:
            print("\tInstructor ID:", instructor[0], "| Name:", instructor[1], instructor[2])

# ADDING FROM USER INPUT
choice = input("Do you want to add a custom course? (y/n): ").strip().lower()

if choice == 'y':
    print("\n--- Manually Add a Custom Course ---")
    ucrn = input("Enter CRN: ")
    utitle = input("Enter Course Title: ")
    udept = input("Enter Department: ") 
    utime = input("Enter Class Time: ")
    udays = input("Enter Days: ")
    usemester = input("Enter Semester: ")
    uyear = input("Enter Year: ")
    ucredits = input("Enter Credits: ")

    # Python 3 compatible execution string injection formatting
    cursor.execute("""INSERT INTO COURSE VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" % (ucrn, utitle, udept, utime, udays, usemester, uyear, ucredits))

    print("\nEntire COURSE table after manual addition:")
    cursor.execute("""SELECT * FROM COURSE""")
    query_result = cursor.fetchall()
    
    for i in query_result:
        print(i)
        
else:
    print("Skipping manual course addition.")

# To save the changes in the files. Never skip this.  
# If we skip this, nothing will be saved in the database. 
database.commit() 
  
# close the connection 
database.close() 