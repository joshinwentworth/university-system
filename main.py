from user import User
from instructor import Instructor
import sqlite3

database = sqlite3.connect('LeopardWeb_Data.db') 
cursor = database.cursor() 
cursor2 = database.cursor() 



def menu(ID, role, user):
    print(" ")
    print("Please select an option") 

    #enter user functions here

    if (role == "Student"):
        #enter stunent functions here
        pass

    elif (role == "Instructor"):
        #enter Instructor functions here
        print ("chouse 3 for your teaching schedule")

        pass

    elif (role == "Admin"):
        #enter Admin functions here
        pass

    option = input("option: ")

    if (option == 1):
        pass
    elif (option == 2):
        pass
    elif (option == "3"):
        user.teaching_schedule(ID)
        
print(" ")
print("Welcome to the University Portal System")
print(" ")
username = input("Username : ")
password = input("Password : ")

# Authenticates identity 
cursor.execute("""SELECT * FROM login""")
query_result = cursor.fetchall()

cursor2.execute("""SELECT * FROM INSTRUCTOR""")
query_result2 = cursor2.fetchall()

for i in query_result:
    if (i[1] == username and i[2] == password):

        print("Access Granted welcome " + str(i[3]))

        #creats the class
        if (i[3] == "Instructor"):
            for i2 in query_result2:
                #print(i2[0])
                #print(i[0])
                if (str(i2[0]) == str(i[0])):
                    #print(3)
                    instructor = Instructor(i2[0], i2[1], i2[2], i2[6], i[3], i2[5])

        menu(i[0], i[3], instructor)
    else:
        pass
        #print("Access Denied")
