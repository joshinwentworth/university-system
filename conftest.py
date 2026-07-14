import sqlite3
import pytest

SCHEMA = """
CREATE TABLE LOGIN (
ID INTEGER PRIMARY KEY NOT NULL,
EMAIL TEXT UNIQUE NOT NULL,
PASSWORD TEXT NOT NULL,
ROLE TEXT NOT NULL);

CREATE TABLE ADMIN (
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
TITLE TEXT NOT NULL,
OFFICE TEXT NOT NULL,
EMAIL TEXT NOT NULL,
FOREIGN KEY(ID) REFERENCES LOGIN(ID));

CREATE TABLE INSTRUCTOR (
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
TITLE TEXT NOT NULL,
HIREYEAR INTEGER NOT NULL,
DEPT CHAR(4) NOT NULL,
EMAIL TEXT NOT NULL,
FOREIGN KEY(ID) REFERENCES LOGIN(ID));

CREATE TABLE STUDENT (
ID INTEGER PRIMARY KEY NOT NULL,
FIRST_NAME TEXT NOT NULL,
LAST_NAME TEXT NOT NULL,
GRADYEAR INTEGER NOT NULL,
MAJOR CHAR(4) NOT NULL,
EMAIL TEXT NOT NULL,
FOREIGN KEY(ID) REFERENCES LOGIN(ID));

CREATE TABLE COURSE (
CRN INTEGER PRIMARY KEY NOT NULL,
TITLE TEXT NOT NULL,
DEPARTMENT TEXT NOT NULL,
TIME TEXT NOT NULL,
DAYS TEXT NOT NULL,
SEMESTER TEXT NOT NULL,
YEAR INTEGER NOT NULL,
CREDITS INTEGER NOT NULL,
INSTRUCTOR_ID INTEGER,
FOREIGN KEY(INSTRUCTOR_ID) REFERENCES INSTRUCTOR(ID));

CREATE TABLE REGISTRATION (
STUDENT_ID INTEGER NOT NULL,
CRN INTEGER NOT NULL,
PRIMARY KEY (STUDENT_ID, CRN),
FOREIGN KEY(STUDENT_ID) REFERENCES STUDENT(ID),
FOREIGN KEY(CRN) REFERENCES COURSE(CRN));
"""


@pytest.fixture
def db_conn():
    """A fresh in-memory SQLite DB matching the LeopardWeb schema, per test."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def seeded_conn(db_conn):
    """db_conn pre-populated with a representative dataset:
    - 1 admin, 2 instructors, 3 students
    - 4 courses (3 with instructor 100, 1 unassigned)
    - a couple of existing registrations
    """
    cur = db_conn.cursor()

    # LOGIN
    cur.executemany(
        "INSERT INTO LOGIN (ID, EMAIL, PASSWORD, ROLE) VALUES (?, ?, ?, ?)",
        [
            (1, "admin@leopardweb.edu", "adminpass", "Admin"),
            (100, "prof.smith@leopardweb.edu", "instpass", "Instructor"),
            (101, "prof.jones@leopardweb.edu", "instpass2", "Instructor"),
            (200, "alice@leopardweb.edu", "studpass", "Student"),
            (201, "bob@leopardweb.edu", "studpass2", "Student"),
            (202, "carol@leopardweb.edu", "studpass3", "Student"),
        ],
    )

    # ADMIN
    cur.execute(
        "INSERT INTO ADMIN (ID, FIRST_NAME, LAST_NAME, TITLE, OFFICE, EMAIL) VALUES (?, ?, ?, ?, ?, ?)",
        (1, "Ada", "Admin", "Registrar", "Room 101", "admin@leopardweb.edu"),
    )

    # INSTRUCTOR
    cur.executemany(
        "INSERT INTO INSTRUCTOR (ID, FIRST_NAME, LAST_NAME, TITLE, HIREYEAR, DEPT, EMAIL) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (100, "John", "Smith", "Professor", 2010, "BCOS", "prof.smith@leopardweb.edu"),
            (101, "Jane", "Jones", "Assistant Prof", 2018, "MATH", "prof.jones@leopardweb.edu"),
        ],
    )

    # STUDENT
    cur.executemany(
        "INSERT INTO STUDENT (ID, FIRST_NAME, LAST_NAME, GRADYEAR, MAJOR, EMAIL) VALUES (?, ?, ?, ?, ?, ?)",
        [
            (200, "Alice", "Anderson", 2027, "BSCO", "alice@leopardweb.edu"),
            (201, "Bob", "Baker", 2026, "BSCO", "bob@leopardweb.edu"),
            (202, "Carol", "Clark", 2028, "MATH", "carol@leopardweb.edu"),
        ],
    )

    # COURSE
    cur.executemany(
        """INSERT INTO COURSE (CRN, TITLE, DEPARTMENT, TIME, DAYS, SEMESTER, YEAR, CREDITS, INSTRUCTOR_ID)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (1001, "Intro to Programming", "BCOS", "10:00", "MWF", "Fall", 2026, 3, 100),
            (1002, "Data Structures", "BCOS", "14:00", "TR", "Fall", 2026, 3, 100),
            (1003, "Calculus I", "MATH", "10:00", "MWF", "Fall", 2026, 4, 101),
            (1004, "Unassigned Seminar", "BCOS", "09:00", "TR", "Fall", 2026, 1, None),
        ],
    )

    # REGISTRATION (Alice already in Intro to Programming; Bob already in Calculus I)
    cur.executemany(
        "INSERT INTO REGISTRATION (STUDENT_ID, CRN) VALUES (?, ?)",
        [
            (200, 1001),
            (201, 1003),
        ],
    )

    db_conn.commit()
    return db_conn
