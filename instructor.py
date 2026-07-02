from user import User
import sqlite3

database = sqlite3.connect('LeopardWeb_Data.db') 
cursor = database.cursor() 

class Instructor(User):
    def __init__(self, id_number, first_name, last_name, email, title, department):
         super().__init__(id_number, first_name, last_name, email, "Instructor")
         self.title = title
         self.department = department

    def teaching_schedule(self, ID):

        cursor.execute("""SELECT * FROM COURSE""")
        query_result = cursor.fetchall()

        for i in query_result:
            #print(i[8])
            #print(ID)
            if (str(i[8]) == str(ID)):
                print(i)

    def students_schedule():
        #add student's function here
        pass