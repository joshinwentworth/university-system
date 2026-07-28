import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from logic import Student, Instructor, Admin, Course
import pytest

class university_system_app(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wentworth university system Simulator")
        
        # Session state variables
        self.current_user = None
        self.user_role = None
        self.user_balance = 0.0

        # In-Memory Balance Cache
        self.session_balances = {}
        
        self.current_frame = None
        
        # Launch directly into the login screen
        self.switch_frame(LoginFrame)

    # Destroys the current frame, resizes the master window, and packs the new frame.
    def switch_frame(self, frame_class, *args, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        # 1. Instantiate the new frame
        self.current_frame = frame_class(self, *args, **kwargs)
        
        # 2. Apply the frame's preferred state (zoomed vs normal)
        if hasattr(self.current_frame, 'target_state'):
            self.state(self.current_frame.target_state)
        else:
            self.state('normal')
            
        # 3. Apply the frame's preferred dimensions (if not zoomed)
        if hasattr(self.current_frame, 'target_geometry') and self.state() != 'zoomed':
            self.geometry(self.current_frame.target_geometry)
            
        # 4. Pack the frame into the master window
        self.current_frame.pack(fill="both", expand=True)

    def return_to_hub(self):
        # Sync current balance to the runtime cache before swapping
        if self.current_user:
            self.session_balances[self.current_user] = self.user_balance
            
        if self.user_role == "Admin":
            self.switch_frame(AdminHubFrame) 
        else:
            self.switch_frame(PlayerHubFrame)

class LoginFrame(tk.Frame):
    target_state = 'normal'
    target_geometry = '400x225'

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        # Username row
        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Password row
        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Login button
        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=15)

        # Create Account Button
        # self.create_acc_button = tk.Button(self, text="Create New Player", width=15, command=self.go_to_create_user)
        # self.create_acc_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Bind enter key and set focus
        self.master.bind("<Return>", self.login)
        self.username_entry.focus()

    def login(self, event=None):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip() 
        
        try:
        
            conn = sqlite3.connect("LeopardWeb_Data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT PASSWORD, ROLE, EMAIL FROM LOGIN WHERE EMAIL = ?", (username,))
            row = cursor.fetchone()
            conn.close()

            #print(row)
            #print(row[0])
            #print(row[2])

        
            if (row and row[0] == password)and(row[2] == username):
                print("correct username and password")
                # Store user data in master controller
                self.master.current_user = username
                self.master.user_role = row[1]
                
                # Check runtime cache. If new session, pull from DB. Otherwise, pull from cache.
                if username not in self.master.session_balances:
                    self.master.session_balances[username] = row[2] # Pull DB starting balance
                    
                self.master.user_balance = self.master.session_balances[username]
                
                # Unbind the enter key so it doesn't trigger in other frames
                self.master.unbind("<Return>")
                
                # Route based on role
                if self.master.user_role == "Admin":
                    self.master.switch_frame(AdminHubFrame)
                elif (self.master.user_role == "Student"):
                    # cursor.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL, GRADYEAR, MAJOR FROM STUDENT WHERE ID = ?", (user_id,))
                    # data = cursor.fetchone()
                    # Student(conn, user_id, data[0], data[1], data[2], data[3], data[4]), role
                    self.master.switch_frame(StudentHubFrame)
                elif (self.master.user_role == "Instructer"):
                    self.master.switch_frame(InstructerHubFrame)
            else:
                messagebox.showerror("Login Failed", "Incorrect username and/or password.")
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                
        except sqlite3.OperationalError:
            messagebox.showerror("Database Error", "Casino_Data.db not found! Run your DB script first.")

    def go_to_create_user(self):
        self.master.unbind("<Return>")
        self.master.switch_frame(CreateUserFrame)


#will become the main menu window
class StudentHubFrame(ttk.Frame): 
    target_state = 'zoomed'

    def __init__(self, master):
        super().__init__(master, padding=20)
        self.master = master
        self.create_gui()

    def create_gui(self):
        # Welcome Header
        welcome_frame = ttk.Frame(self)
        welcome_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(welcome_frame, text=f"Welcome {self.master.current_user}!", font=("Arial", 18, "bold")).pack()
        ttk.Label(welcome_frame, text="Select a function below", font=("Arial", 12)).pack()

        # Balance display
        # balance_frame = ttk.Frame(self)
        # balance_frame.pack(fill=tk.X, pady=(0, 15))
        # ttk.Label(balance_frame, text=f"Current Balance: ${self.master.user_balance:,.2f}", font=("Arial", 16, "bold")).pack()

        # Buttons Grid
        Buttons_frame = ttk.LabelFrame(self, text="Functions", padding=15, width=200)
        Buttons_frame.pack(side=tk.LEFT,fill=tk.BOTH, expand=True, pady=10)
        Buttons_frame.pack_propagate(False)

        # Results Grid
        Results_frame = ttk.LabelFrame(self, text="Text", padding=15)
        Results_frame.pack(side=tk.LEFT,fill=tk.BOTH, expand=True, pady=10)

        btn_row = 0
        btn_col = 0

        label_info = tk.Label(Results_frame, text="                                                              ", font=("Arial", 11, "bold"), fg="black")
        label_info.pack()

        for i in range(6):
            ttk.Button(Buttons_frame, text="button text", command=lambda: test_print(label_info)).grid(row=btn_row, column=btn_col, padx=15, pady=12, ipadx=10, ipady=8)
            btn_row += 1

        # Logout Button
        ttk.Button(self, text="Logout", command=self.logout).pack(side="bottom", pady=20)

    # def open_game(self, game_name: str):
    #     """Route to the correct game frame"""
    #     if game_name == "Keno":
    #         try:
    #             from Games.Keno.Keno import KenoGameFrame
    #         except ImportError:
    #             messagebox.showinfo("Error", "Keno file not found.")
    #         self.master.switch_frame(KenoGameFrame)
    #     elif game_name == "Slots":
    #         try:
    #             from Games.Slots.Slots import SlotsGameFrame
    #             self.master.switch_frame(SlotsGameFrame)
    #         except ImportError:
    #             messagebox.showinfo("Error", "Slots file not found.")
    #     elif game_name == "Roulette":
    #         try:
    #             from Games.Roulette.Roulette import RouletteGameFrame
    #         except ImportError:
    #             messagebox.showinfo("Error", "Roulette file not found.")
    #         self.master.switch_frame(RouletteGameFrame)
    #     elif game_name == "Bingo":
    #         try:
    #             from Games.Bingo.Bingo import BingoGameFrame
    #         except ImportError:
    #             messagebox.showinfo("Error", "Bingo file not found.")
    #         self.master.switch_frame(BingoGameFrame)
    #     elif game_name == "Kla-Klok":
    #         try:
    #             from Games.Kla_Klok.Kla_Klok import KlaKlokGameFrame
    #         except ImportError:
    #             messagebox.showinfo("Error", "Kla-Klok file not found.")
    #         self.master.switch_frame(KlaKlokGameFrame)
    #     else:
    #         messagebox.showinfo("Coming Soon", f"{game_name} is not implemented yet.")

    def logout(self):
        # Sync to cache before logging out
        if self.master.current_user:
            self.master.session_balances[self.master.current_user] = self.master.user_balance
            
        self.master.current_user = None
        self.master.user_balance = 0.0
        self.master.switch_frame(LoginFrame)

def test_print(label_info):
    current_text = label_info.cget("text")
    label_info.config(text = " \n" + current_text)
    current_text = label_info.cget("text")
    label_info.config(text = "test" + current_text)

# Not used for gui
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

# if __name__ == "__main__":
#     main()


# def test_something_that_involves_user_input(main):

#     main.setattr('builtins.input', lambda _: "Mark")
#     email = input("Email: ")
#     assert email == "Mark"

if __name__ == "__main__":
    app = university_system_app()
    app.mainloop()
