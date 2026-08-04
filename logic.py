import sqlite3
#from main import gui_print

def gui_print(label_info, text_to_be_printed):
    current_text = label_info.cget("text")
    label_info.config(text = current_text+" \n")
    current_text = label_info.cget("text")
    label_info.config(text =  current_text + text_to_be_printed)

class Course:
    def __init__(self, crn, title, dept, time, days, semester, year, credits, instructor_id=None):
        self.crn = crn
        self.title = title
        self.dept = dept
        self.time = time
        self.days = days
        self.semester = semester
        self.year = year
        self.credits = credits
        self.instructor_id = instructor_id

    def __str__(self):
        return f"[{self.crn}] {self.title} ({self.dept}) | {self.days} at {self.time} | {self.credits} Credits"

class User:
    def __init__(self, db_conn, user_id, first_name, last_name, email):
        self.conn = db_conn
        self.cursor = db_conn.cursor()
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def search_courses(self, label_info, param=None):

        print("pram in search_courses: "+str(param))

        if param:
            self.cursor.execute("SELECT * FROM COURSE WHERE TITLE LIKE ? OR DEPARTMENT LIKE ?", (f'%{param}%', f'%{param}%'))
        else:
            self.cursor.execute("SELECT * FROM COURSE")
        
        results = self.cursor.fetchall()
        courses = [Course(*row) for row in results]
        print("\n--- Course Search Results ---")
        gui_print(label_info, "--- Course Search Results ---")
        for c in courses:
            print(c)
            gui_print(label_info, str(c))
            
        return courses

class Student(User):
    def __init__(self, db_conn, user_id, first_name, last_name, email, grad_year, major):
        super().__init__(db_conn, user_id, first_name, last_name, email)
        self.grad_year = grad_year
        self.major = major

    def _get_schedule(self):
        self.cursor.execute("""
            SELECT C.* FROM COURSE C
            JOIN REGISTRATION R ON C.CRN = R.CRN
            WHERE R.STUDENT_ID = ?
        """, (self.user_id,))
        return [Course(*row) for row in self.cursor.fetchall()]

    def check_conflicts(self, new_course):
        current_courses = self._get_schedule()
        
        # Calculate new course time block
        new_start = int(new_course.time)
        new_duration = int(new_course.credits / len(new_course.days))
        new_end = new_start + new_duration
        new_days = set(new_course.days)

        for course in current_courses:
            # Calculate current course time block
            curr_start = int(course.time)
            curr_duration = int(course.credits / len(course.days))
            curr_end = curr_start + curr_duration
            curr_days = set(course.days)

            # Check if there is any overlapping days
            if new_days.intersection(curr_days):
                # Check if times overlap
                if max(new_start, curr_start) < min(new_end, curr_end):
                    return True
        return False

    def add_course(self, label_info, crn):
        self.cursor.execute("SELECT * FROM COURSE WHERE CRN = ?", (crn,))
        row = self.cursor.fetchone()
        if not row:
            gui_print(label_info, "Error: Course not found.")
            print("Error: Course not found.")
            return

        new_course = Course(*row)
        if self.check_conflicts(new_course):
            gui_print(label_info, "Error: Schedule conflict detected! Cannot add course.")
            print("Error: Schedule conflict detected! Cannot add course.")
            return

        try:
            self.cursor.execute("INSERT INTO REGISTRATION VALUES (?, ?)", (self.user_id, crn))
            self.conn.commit()
            gui_print(label_info, f"Successfully added {new_course.title} to your schedule.")
            print(f"Successfully added {new_course.title} to your schedule.")
        except:
            gui_print(label_info, "You are already enrolled in this course.")
            print("You are already enrolled in this course.")

    def remove_course(self, label_info, crn):
        self.cursor.execute("DELETE FROM REGISTRATION WHERE STUDENT_ID = ? AND CRN = ?", (self.user_id, crn))
        self.conn.commit()
        gui_print(label_info, "Course removed from schedule (if you were enrolled).")
        print("Course removed from schedule (if you were enrolled).")

    def print_schedule(self, label_info):
        courses = self._get_schedule()
        gui_print(label_info, "--- Your Class Schedule ---")
        print("\n--- Your Class Schedule ---")
        if not courses:
            gui_print(label_info, "You are not enrolled in any courses.")
            print("You are not enrolled in any courses.")
        for c in courses:
            gui_print(label_info, str(c))
            print(str(c))

class Instructor(User):
    def __init__(self, db_conn, user_id, first_name, last_name, email, title, hire_year, dept):
        super().__init__(db_conn, user_id, first_name, last_name, email)
        self.title = title
        self.hire_year = hire_year
        self.dept = dept

    def print_teaching_schedule(self, label_info):
        self.cursor.execute("SELECT * FROM COURSE WHERE INSTRUCTOR_ID = ?", (self.user_id,))
        courses = [Course(*row) for row in self.cursor.fetchall()]
        gui_print(label_info, "--- Your Teaching Schedule ---")
        print("\n--- Your Teaching Schedule ---")
        if not courses:
            gui_print(label_info, "You are not assigned to teach any courses.")
            print("You are not assigned to teach any courses.")
        for c in courses:
            gui_print(label_info, str(c))
            print(c)

    def print_roster(self, label_info, crn):
        self.cursor.execute("""
            SELECT S.FIRST_NAME, S.LAST_NAME, S.EMAIL FROM STUDENT S
            JOIN REGISTRATION R ON S.ID = R.STUDENT_ID
            JOIN COURSE C ON R.CRN = C.CRN
            WHERE C.CRN = ? AND C.INSTRUCTOR_ID = ?
        """, (crn, self.user_id))
        students = self.cursor.fetchall()
        gui_print(label_info, f"--- General Roster for CRN {crn} ---")
        print(f"\n--- General Roster for CRN {crn} ---")
        if not students:
            gui_print(label_info, "No students enrolled or you do not teach this course.")
            print("No students enrolled or you do not teach this course.")
        for s in students:
            gui_print(label_info, f"{s[0]} {s[1]} ({s[2]})")
            print(f"{s[0]} {s[1]} ({s[2]})")

    def search_roster(self, crn, search_keyword):
        self.cursor.execute("""
            SELECT S.FIRST_NAME, S.LAST_NAME, S.EMAIL FROM STUDENT S
            JOIN REGISTRATION R ON S.ID = R.STUDENT_ID
            JOIN COURSE C ON R.CRN = C.CRN
            WHERE C.CRN = ? AND C.INSTRUCTOR_ID = ? AND (S.FIRST_NAME LIKE ? OR S.LAST_NAME LIKE ?)
        """, (crn, self.user_id, f'%{search_keyword}%', f'%{search_keyword}%'))
        students = self.cursor.fetchall()
        print(f"\n--- Search Results for '{search_keyword}' in CRN {crn} ---")
        if not students:
            print("No matching students found in this course.")
        for s in students:
            print(f"{s[0]} {s[1]} ({s[2]})")

class Admin(User):
    def __init__(self, db_conn, user_id, first_name, last_name, email, title, office):
        super().__init__(db_conn, user_id, first_name, last_name, email)
        self.title = title
        self.office = office

    def add_course(self, label_info, course_obj):
        try:
            self.cursor.execute("""
                INSERT INTO COURSE (CRN, TITLE, DEPARTMENT, TIME, DAYS, SEMESTER, YEAR, CREDITS, INSTRUCTOR_ID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (course_obj.crn, course_obj.title, course_obj.dept, course_obj.time, 
                  course_obj.days, course_obj.semester, course_obj.year, course_obj.credits, course_obj.instructor_id))
            self.conn.commit()
            gui_print(label_info, "Course successfully added to the system.")
            print("Course successfully added to the system.")
        except Exception as e:
            gui_print(label_info, f"--- Global Roster for CRN {crn} ---")
            print(f"Error adding course: {e}")

    def print_roster(self, label_info, crn):
        self.cursor.execute("""
            SELECT S.FIRST_NAME, S.LAST_NAME, S.EMAIL FROM STUDENT S
            JOIN REGISTRATION R ON S.ID = R.STUDENT_ID
            WHERE R.CRN = ?
        """, (crn,))
        students = self.cursor.fetchall()
        gui_print(label_info, f"--- Global Roster for CRN {crn} ---")
        print(f"\n--- Global Roster for CRN {crn} ---")
        if not students:
            gui_print(label_info, "No students enrolled in this course.")
            print("No students enrolled in this course.")
        for s in students:
            gui_print(label_info, f"{s[0]} {s[1]} ({s[2]})")
            print(f"{s[0]} {s[1]} ({s[2]})")

    def link_instructor(self, crn, instructor_id):
        if instructor_id is None:
            self.cursor.execute("UPDATE COURSE SET INSTRUCTOR_ID = NULL WHERE CRN = ?", (crn,))
            print(f"Instructor unlinked from course {crn}.")
        else:
            self.cursor.execute("UPDATE COURSE SET INSTRUCTOR_ID = ? WHERE CRN = ?", (instructor_id, crn))
            print(f"Instructor {instructor_id} linked to course {crn}.")
        self.conn.commit()
        
    def manage_student_enrollment(self, student_id, crn, action):
        if action == "add":
            try:
                self.cursor.execute("INSERT INTO REGISTRATION VALUES (?, ?)", (student_id, crn))
                print(f"Student {student_id} added to course {crn}.")
            except:
                print("Student already enrolled.")
        elif action == "remove":
            self.cursor.execute("DELETE FROM REGISTRATION WHERE STUDENT_ID = ? AND CRN = ?", (student_id, crn))
            print(f"Student {student_id} removed from course {crn}.")
        self.conn.commit()

    def add_user(self, role, first_name, last_name, email, password, **kwargs):
        try:
            self.cursor.execute("SELECT MAX(ID) FROM LOGIN")
            max_id_row = self.cursor.fetchone()
            new_id = (max_id_row[0] + 1) if max_id_row[0] else 1

            self.cursor.execute("INSERT INTO LOGIN (ID, EMAIL, PASSWORD, ROLE) VALUES (?, ?, ?, ?)", 
                                (new_id, email, password, role))
            
            if role == 'Student':
                self.cursor.execute("INSERT INTO STUDENT (ID, FIRST_NAME, LAST_NAME, GRADYEAR, MAJOR, EMAIL) VALUES (?, ?, ?, ?, ?, ?)",
                                    (new_id, first_name, last_name, kwargs.get('grad_year'), kwargs.get('major'), email))
            elif role == 'Instructor':
                self.cursor.execute("INSERT INTO INSTRUCTOR (ID, FIRST_NAME, LAST_NAME, TITLE, HIREYEAR, DEPT, EMAIL) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (new_id, first_name, last_name, kwargs.get('title'), kwargs.get('hire_year'), kwargs.get('dept'), email))
            self.conn.commit()
            print(f"Successfully added {role}: {first_name} {last_name} with ID {new_id}.")
        except sqlite3.IntegrityError:
            print("Error: A user with this email already exists in the system.")
        except Exception as e:
            print(f"Error adding user: {e}")