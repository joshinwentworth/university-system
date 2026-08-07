import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from logic import Student, Instructor, Admin, Course

logged_in_user = None

# setting up the main window and top menu
class LeopardWebRegistrationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WIT LeopardWeb Registration System")
        
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        
        toolbar_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Toolbar", menu=toolbar_menu)
        toolbar_menu.add_command(label="Help", command=self.show_help)
        toolbar_menu.add_command(label="About", command=self.show_about)

        self.current_user = None
        self.user_role = None
        self.user_id = None
        self.current_frame = None
        
        self.switch_frame(LoginFrame)

    def show_help(self):
        messagebox.showinfo("Help", "Enter your Wentworth email and password to log in.\n"
                            "Click the function buttons to open specific prompts.\n"
                            "Parameter settings will appear once a function is selected\n\n"
                            "All information should be entered in the following format:\n"
                            "Department or Major: BSCO, BSEE, COMP, ARCH, CONM, MATH, PHYS, ENGL\n"
                            "Time: Military time in hours (e.g. 08 or 14)\n"
                            "Days: MTWRF\n"
                            "Semester: Fall, Spring, or Summer\n"
                            "Year: 20XX\n"
                            "Credits: If 3 credits... list as 1 or 3 days per week, If 4 credits... list as 1, 2, or 4 days per week\n"
                            "Instructor Title: Professor, Associate Professor, or Assistant Professor")

    def show_about(self):
        messagebox.showinfo("About", "WIT LeopardWeb Registration System\nGroup Members: Hayden Pierce, Josh Kolasa")

    # swap between login and whatever hub they need without making a new window
    def switch_frame(self, frame_class, *args, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = frame_class(self, *args, **kwargs)
        
        if hasattr(self.current_frame, 'target_state'):
            self.state(self.current_frame.target_state)
        else:
            self.state('normal')
            
        if hasattr(self.current_frame, 'target_geometry') and self.state() != 'zoomed':
            self.geometry(self.current_frame.target_geometry)
            
        self.current_frame.pack(fill="both", expand=True)

class LoginFrame(tk.Frame):
    target_state = 'normal'
    target_geometry = '400x250'

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        self.username_label = tk.Label(self, text="Email:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.login_button = tk.Button(self, text="Login", command=self.login, width=15)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.forgot_btn = tk.Button(self, text="Forgot Password", command=self.forgot_password, width=15)
        self.forgot_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.master.bind("<Return>", self.login)
        self.username_entry.focus()

    # check db for user and build their specific object type
    def login(self, event=None):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip() 
        
        conn = sqlite3.connect("LeopardWeb_Data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT PASSWORD, ROLE, EMAIL, ID FROM LOGIN WHERE EMAIL = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row and row[0] == password and row[2] == username:
            self.master.current_user = username
            self.master.user_role = row[1]
            self.master.user_id = row[3]

            self.master.unbind("<Return>")
            global logged_in_user
            
            conn2 = sqlite3.connect("LeopardWeb_Data.db")
            cursor2 = conn2.cursor()
            
            # map them to the correct dashboard based on role
            if self.master.user_role == "Admin":
                cursor2.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL, TITLE, OFFICE FROM ADMIN WHERE ID = ?", (self.master.user_id,))
                data = cursor2.fetchone()
                logged_in_user = Admin(conn2, self.master.user_id, data[0], data[1], data[2], data[3], data[4])
                self.master.switch_frame(AdminHubFrame)
            elif self.master.user_role == "Student":
                cursor2.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL, GRADYEAR, MAJOR FROM STUDENT WHERE ID = ?", (self.master.user_id,))
                data = cursor2.fetchone()
                logged_in_user = Student(conn2, self.master.user_id, data[0], data[1], data[2], data[3], data[4])
                self.master.switch_frame(StudentHubFrame)
            elif self.master.user_role == "Instructor":
                cursor2.execute("SELECT FIRST_NAME, LAST_NAME, EMAIL, TITLE, HIREYEAR, DEPT FROM INSTRUCTOR WHERE ID = ?", (self.master.user_id,))
                data = cursor2.fetchone()
                logged_in_user = Instructor(conn2, self.master.user_id, data[0], data[1], data[2], data[3], data[4], data[5])
                self.master.switch_frame(InstructorHubFrame)
                
        else:
            messagebox.showerror("Login Failed", "Incorrect email or password.")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def forgot_password(self):
        messagebox.showinfo("Reset Password", "Please contact admin to reset your password.")

class StudentHubFrame(ttk.Frame): 
    target_state = 'zoomed'

    def __init__(self, master):
        super().__init__(master, padding=20)
        self.master = master
        self.create_gui()

    # set up the buttons on the left and the big output window on the right
    def create_gui(self):
        welcome_frame = ttk.Frame(self)
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(welcome_frame, text=f"Welcome {logged_in_user.first_name} {logged_in_user.last_name}!", font=("Arial", 18, "bold")).pack()
        ttk.Label(welcome_frame, text="Select a function below", font=("Arial", 12)).pack()

        Buttons_frame = ttk.LabelFrame(self, text="Functions", padding=15, width=250)
        Buttons_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, pady=10)
        Buttons_frame.pack_propagate(False)

        Results_frame = ttk.LabelFrame(self, text="System Output", padding=15)
        Results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=(10, 0))

        self.label_info = tk.Text(Results_frame, wrap=tk.WORD, font=("Consolas", 10), state="disabled", bg="#f9f9f9")
        scrollbar = ttk.Scrollbar(Results_frame, command=self.label_info.yview)
        self.label_info.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.label_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label_info.tag_configure("title", font=("Consolas", 11, "bold"), foreground="#003366")
        self.label_info.tag_configure("error", font=("Consolas", 10, "bold"), foreground="#cc0000")

        ttk.Button(Buttons_frame, text="Search All Courses", command=lambda: logged_in_user.search_courses(self.label_info)).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Search Courses by Param", command=self.search_param_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Add Course to Schedule", command=self.add_course_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Remove Course from Schedule", command=self.remove_course_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Print Schedule", command=lambda: logged_in_user.print_schedule(self.label_info)).pack(fill=tk.X, pady=5)

        ttk.Button(Buttons_frame, text="Logout", command=self.logout).pack(side=tk.BOTTOM, fill=tk.X, pady=20)

    def search_param_action(self):
        param = simpledialog.askstring("Search Courses", "          Enter search keyword (Title or Dept):          ")
        if param is not None:
            param_clean = param.strip()
            if param_clean:
                logged_in_user.search_courses(self.label_info, param_clean)
            else:
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")

    def add_course_action(self):
        crn_str = simpledialog.askstring("Add Course", "Enter the CRN to add:")
        if crn_str is not None:
            crn_clean = crn_str.strip()
            if crn_clean.isdigit():
                logged_in_user.add_course(self.label_info, int(crn_clean))
            elif crn_clean == "":
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            else:
                messagebox.showerror("Invalid Input", "CRN must be a valid numeric integer.")

    def remove_course_action(self):
        crn_str = simpledialog.askstring("Remove Course", "Enter the CRN to remove:")
        if crn_str is not None:
            crn_clean = crn_str.strip()
            if crn_clean.isdigit():
                logged_in_user.remove_course(self.label_info, int(crn_clean))
            elif crn_clean == "":
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            else:
                messagebox.showerror("Invalid Input", "CRN must be a valid numeric integer.")

    def logout(self):
        self.master.current_user = None
        self.master.switch_frame(LoginFrame)

class InstructorHubFrame(ttk.Frame): 
    target_state = 'zoomed'

    def __init__(self, master):
        super().__init__(master, padding=20)
        self.master = master
        self.create_gui()

    def create_gui(self):
        welcome_frame = ttk.Frame(self)
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(welcome_frame, text=f"Welcome {logged_in_user.first_name} {logged_in_user.last_name}!", font=("Arial", 18, "bold")).pack()
        ttk.Label(welcome_frame, text="Select a function below", font=("Arial", 12)).pack()

        Buttons_frame = ttk.LabelFrame(self, text="Functions", padding=15, width=250)
        Buttons_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, pady=10)
        Buttons_frame.pack_propagate(False)

        Results_frame = ttk.LabelFrame(self, text="System Output", padding=15)
        Results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=(10, 0))

        self.label_info = tk.Text(Results_frame, wrap=tk.WORD, font=("Consolas", 10), state="disabled", bg="#f9f9f9")
        scrollbar = ttk.Scrollbar(Results_frame, command=self.label_info.yview)
        self.label_info.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.label_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label_info.tag_configure("title", font=("Consolas", 11, "bold"), foreground="#003366")
        self.label_info.tag_configure("error", font=("Consolas", 10, "bold"), foreground="#cc0000")

        ttk.Button(Buttons_frame, text="Search All Courses", command=lambda: logged_in_user.search_courses(self.label_info)).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Search Courses by Param", command=self.search_param_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Print Teaching Schedule", command=lambda: logged_in_user.print_teaching_schedule(self.label_info)).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Print Course Roster", command=self.print_roster_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Search Course Roster", command=self.search_roster_action).pack(fill=tk.X, pady=5)

        ttk.Button(Buttons_frame, text="Logout", command=self.logout).pack(side=tk.BOTTOM, fill=tk.X, pady=20)

    def search_param_action(self):
        param = simpledialog.askstring("Search Courses", "          Enter search keyword (Title or Dept):          ")
        if param is not None:
            param_clean = param.strip()
            if param_clean:
                logged_in_user.search_courses(self.label_info, param_clean)
            else:
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")

    def print_roster_action(self):
        crn_str = simpledialog.askstring("Print Roster", "                         Enter the CRN:                         ")
        if crn_str is not None:
            crn_clean = crn_str.strip()
            if crn_clean.isdigit():
                logged_in_user.print_roster(self.label_info, int(crn_clean))
            elif crn_clean == "":
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            else:
                messagebox.showerror("Invalid Input", "CRN must be a valid numeric integer.")

    def search_roster_action(self):
        crn_str = simpledialog.askstring("Search Roster", "                         Enter the CRN:                         ")
        if crn_str is not None:
            crn_clean = crn_str.strip()
            if crn_clean.isdigit():
                self.master.update()
                keyword = simpledialog.askstring("Search Roster", "          Enter student's first or last name:          ")
                if keyword is not None:
                    key_clean = keyword.strip()
                    if key_clean:
                        logged_in_user.search_roster(self.label_info, int(crn_clean), key_clean)
                    else:
                        messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            elif crn_clean == "":
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            else:
                messagebox.showerror("Invalid Input", "CRN must be a valid numeric integer.")

    def logout(self):
        self.master.current_user = None
        self.master.switch_frame(LoginFrame)

class AdminHubFrame(ttk.Frame): 
    target_state = 'zoomed'

    def __init__(self, master):
        super().__init__(master, padding=20)
        self.master = master
        self.create_gui()

    def create_gui(self):
        welcome_frame = ttk.Frame(self)
        welcome_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(welcome_frame, text=f"Welcome {logged_in_user.first_name} {logged_in_user.last_name}!", font=("Arial", 18, "bold")).pack()
        ttk.Label(welcome_frame, text="Select a function below", font=("Arial", 12)).pack()

        Buttons_frame = ttk.LabelFrame(self, text="Functions", padding=15, width=250)
        Buttons_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, pady=10)
        Buttons_frame.pack_propagate(False)

        Results_frame = ttk.LabelFrame(self, text="System Output", padding=15)
        Results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10, padx=(10, 0))

        self.label_info = tk.Text(Results_frame, wrap=tk.WORD, font=("Consolas", 10), state="disabled", bg="#f9f9f9")
        scrollbar = ttk.Scrollbar(Results_frame, command=self.label_info.yview)
        self.label_info.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.label_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label_info.tag_configure("title", font=("Consolas", 11, "bold"), foreground="#003366")
        self.label_info.tag_configure("error", font=("Consolas", 10, "bold"), foreground="#cc0000")

        ttk.Button(Buttons_frame, text="Search All Courses", command=lambda: logged_in_user.search_courses(self.label_info)).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Search Courses by Param", command=self.search_param_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Print Course Roster", command=self.print_roster_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Search Course Roster", command=self.search_roster_action).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Add New Course", command=self.add_course_popup).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Link/Unlink Instructor", command=self.link_instructor_popup).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Link/Unlink Student", command=self.link_student_popup).pack(fill=tk.X, pady=5)
        ttk.Button(Buttons_frame, text="Add New User", command=self.add_user_popup).pack(fill=tk.X, pady=5)

        ttk.Button(Buttons_frame, text="Logout", command=self.logout).pack(side=tk.BOTTOM, fill=tk.X, pady=20)

    def search_param_action(self):
        param = simpledialog.askstring("Search Courses", "          Enter search keyword (Title or Dept):          ")
        if param is not None:
            param_clean = param.strip()
            if param_clean:
                logged_in_user.search_courses(self.label_info, param_clean)
            else:
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")

    def print_roster_action(self):
        crn_str = simpledialog.askstring("Print Roster", "                         Enter the CRN:                         ")
        if crn_str is not None:
            crn_clean = crn_str.strip()
            if crn_clean.isdigit():
                logged_in_user.print_roster(self.label_info, int(crn_clean))
            elif crn_clean == "":
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            else:
                messagebox.showerror("Invalid Input", "CRN must be a valid numeric integer.")

    def search_roster_action(self):
        crn_str = simpledialog.askstring("Search Roster", "                         Enter the CRN:                         ")
        if crn_str is not None:
            crn_clean = crn_str.strip()
            if crn_clean.isdigit():
                self.master.update()
                keyword = simpledialog.askstring("Search Roster", "          Enter student's first or last name:          ")
                if keyword is not None:
                    key_clean = keyword.strip()
                    if key_clean:
                        logged_in_user.search_roster(self.label_info, int(crn_clean), key_clean)
                    else:
                        messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            elif crn_clean == "":
                messagebox.showwarning("Invalid Input", "Parameter cannot be left blank.")
            else:
                messagebox.showerror("Invalid Input", "CRN must be a valid numeric integer.")

    # building custom popup for adding a course
    def add_course_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add New Course")
        popup.geometry("320x350")
        popup.grab_set() 
        
        entries = {}
        fields = ["CRN", "Title", "Department", "Time", "Days", "Semester", "Year", "Credits", "Instructor ID (Optional)"]
        
        for i, field in enumerate(fields):
            tk.Label(popup, text=field + ":").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            ent = tk.Entry(popup)
            ent.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = ent
            
        def submit():
            try:
                title = entries["Title"].get().strip().title()
                dept = entries["Department"].get().strip().upper()
                time = entries["Time"].get().strip()
                days = entries["Days"].get().strip().upper()
                sem = entries["Semester"].get().strip().capitalize()
                
                if not all([title, dept, time, days, sem]):
                    messagebox.showwarning("Missing Information", "Please complete all required fields before submitting.", parent=popup)
                    return
                
                crn = int(entries["CRN"].get())
                
                # check if CRN already exists
                conn = sqlite3.connect("LeopardWeb_Data.db")
                cursor = conn.cursor()
                cursor.execute("SELECT CRN FROM COURSE WHERE CRN = ?", (crn,))
                if cursor.fetchone():
                    messagebox.showerror("Duplicate Entry", f"CRN {crn} is already assigned to an existing course.", parent=popup)
                    conn.close()
                    return
                conn.close()
                
                year = int(entries["Year"].get())
                cred = int(entries["Credits"].get())
                inst_val = entries["Instructor ID (Optional)"].get().strip()
                inst_id = int(inst_val) if inst_val else None
                
                new_course = Course(crn, title, dept, time, days, sem, year, cred, inst_id)
                logged_in_user.add_course(self.label_info, new_course)
                popup.destroy()
            except ValueError:
                messagebox.showerror("Invalid Data Type", "CRN, Time (hour), Year, and Credits must be numbers.", parent=popup)
                
        tk.Button(popup, text="Submit", command=submit).grid(row=len(fields), column=0, columnspan=2, pady=15)

    def link_instructor_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Link/UnLink")
        popup.grab_set()
        
        tk.Label(popup, text="Instructor ID:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        inst_ent = tk.Entry(popup)
        inst_ent.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="CRN:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        crn_ent = tk.Entry(popup)
        crn_ent.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Action (add/remove):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        act_ent = tk.Entry(popup)
        act_ent.grid(row=2, column=1, padx=10, pady=5)
        
        def submit():
            inst_str = inst_ent.get().strip()
            crn_str = crn_ent.get().strip()
            action = act_ent.get().strip().lower()

            if not all([crn_str, action]):
                messagebox.showwarning("Missing Information", "Please complete all required fields before submitting.", parent=popup)
                return
            
            if action not in ["add", "remove"]:
                messagebox.showerror("Invalid Input", "Action must be add or remove.", parent=popup)
                return
            
            if not crn_str.isdigit():
                messagebox.showerror("Invalid Data Type", "IDs and CRNs must be valid numbers.", parent=popup)
                return
            
            inst_id = int(inst_str) if inst_str.isdigit() else None
            
            if action == "add" and inst_id is None:
                messagebox.showerror("Invalid Data Type", "IDs and CRNs must be valid numbers.", parent=popup)
                return
            
            logged_in_user.link_instructor(self.label_info, inst_id, int(crn_str), action)
            popup.destroy()
            
        tk.Button(popup, text="Submit", command=submit).grid(row=3, column=0, columnspan=2, pady=15)

    def link_student_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Link/UnLink")
        popup.grab_set()
        
        tk.Label(popup, text="Student ID:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        stu_ent = tk.Entry(popup)
        stu_ent.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="CRN:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        crn_ent = tk.Entry(popup)
        crn_ent.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Action (add/remove):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        act_ent = tk.Entry(popup)
        act_ent.grid(row=2, column=1, padx=10, pady=5)
        
        def submit():
            stu_str = stu_ent.get().strip()
            crn_str = crn_ent.get().strip()
            action = act_ent.get().strip().lower()

            if not all([stu_str, crn_str, action]):
                messagebox.showwarning("Missing Information", "Please complete all required fields before submitting.", parent=popup)
                return

            if action not in ["add", "remove"]:
                messagebox.showerror("Invalid Input", "Action must be add or remove.", parent=popup)
                return

            if not stu_str.isdigit() or not crn_str.isdigit():
                messagebox.showerror("Invalid Data Type", "IDs and CRNs must be valid numbers.", parent=popup)
                return
            
            logged_in_user.manage_student_enrollment(self.label_info, int(stu_str), int(crn_str), action)
            popup.destroy()
            
        tk.Button(popup, text="Submit", command=submit).grid(row=3, column=0, columnspan=2, pady=15)

    def add_user_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Add New User")
        popup.grab_set()
        
        tk.Label(popup, text="Role:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        role_ent = tk.Entry(popup)
        role_ent.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="First Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        fn_ent = tk.Entry(popup)
        fn_ent.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Last Name:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        ln_ent = tk.Entry(popup)
        ln_ent.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Expected Grad Year (Student):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        gy_ent = tk.Entry(popup)
        gy_ent.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Major (Student):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        maj_ent = tk.Entry(popup)
        maj_ent.grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Title (Instructor):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        title_ent = tk.Entry(popup)
        title_ent.grid(row=5, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Hire Year (Instructor):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        hy_ent = tk.Entry(popup)
        hy_ent.grid(row=6, column=1, padx=10, pady=5)
        
        tk.Label(popup, text="Department (Instructor):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        dept_ent = tk.Entry(popup)
        dept_ent.grid(row=7, column=1, padx=10, pady=5)
        
        def submit():
            role = role_ent.get().strip().capitalize()
            fn = fn_ent.get().strip().capitalize()
            ln = ln_ent.get().strip().capitalize()
            
            if role not in ["Student", "Instructor"]:
                messagebox.showerror("Invalid Input", "Role must be Student or Instructor.", parent=popup)
                return
            
            try:
                # auto-gen unique emails by checking the db in a loop
                base_prefix = f"{ln.lower()}{fn[0].lower()}"
                email = f"{base_prefix}@wit.edu"
                counter = 1
                
                conn = sqlite3.connect("LeopardWeb_Data.db")
                cursor = conn.cursor()
                while True:
                    cursor.execute("SELECT EMAIL FROM LOGIN WHERE EMAIL = ?", (email,))
                    if not cursor.fetchone():
                        break # if slot is empty, break out of loop
                    
                    email = f"{base_prefix}{counter}@wit.edu" # if slot is taken, add counter and check again
                    counter += 1
                conn.close()
                
                if role == "Student":
                    gy_str = gy_ent.get().strip()
                    maj = maj_ent.get().strip().upper()
                    
                    if not all([fn, ln, gy_str, maj]):
                        messagebox.showwarning("Missing Information", "Please complete all required fields before submitting.", parent=popup)
                        return
                    
                    gy = int(gy_str)
                    pw = f"{fn[0]}{ln[0]}{maj.lower()}{gy % 100}!"
                    
                    logged_in_user.add_user(self.label_info, role, fn, ln, email, pw, grad_year=gy, major=maj)
                
                else:
                    hy_str = hy_ent.get().strip()
                    title = title_ent.get().strip().title()
                    dept = dept_ent.get().strip().upper()
                    
                    if not all([fn, ln, hy_str, title, dept]):
                        messagebox.showwarning("Missing Information", "Please complete all required fields before submitting.", parent=popup)
                        return
                        
                    hy = int(hy_str)
                    pw = f"{fn[0]}{ln[0]}{dept.lower()}{hy % 100}!"
                    
                    logged_in_user.add_user(self.label_info, role, fn, ln, email, pw, title=title, hire_year=hy, dept=dept)
                
                popup.destroy()
            except ValueError:
                messagebox.showerror("Invalid Data Type", "Graduation Year / Hire Year must be a valid number.", parent=popup)
                
        tk.Button(popup, text="Submit", command=submit).grid(row=8, column=0, columnspan=2, pady=15)

    def logout(self):
        self.master.current_user = None
        self.master.switch_frame(LoginFrame)

if __name__ == "__main__":
    app = LeopardWebRegistrationApp()
    app.mainloop()