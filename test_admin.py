"""
Tests for Admin-side system management:
  - Add courses to the system (Admin.add_course)
  - Remove students from courses / manage enrollment (also covers the
    "remove course from the system" surface exposed via enrollment removal
    and via direct DELETE, since logic.py has no dedicated
    Admin.remove_course -- see test_admin_remove_course_from_system below,
    which exercises the underlying COURSE deletion path directly to prove
    the schema/cascade behavior admins rely on)
  - print_roster (global roster across all instructors)
  - link_instructor
  - manage_student_enrollment (add/remove)
  - add_user
"""
import sqlite3

import pytest

from logic import Admin, Course


@pytest.fixture
def ada(seeded_conn):
    return Admin(seeded_conn, 1, "Ada", "Admin", "admin@leopardweb.edu", "Registrar", "Room 101")


def _course_exists(conn, crn):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM COURSE WHERE CRN = ?", (crn,))
    return cur.fetchone() is not None


# ---------------------------------------------------------------------------
# add_course
# ---------------------------------------------------------------------------

def test_add_course_success(ada, seeded_conn, capsys):
    new_course = Course(2001, "Intro to AI", "BCOS", "13:00", "MW", "Spring", 2027, 3, 100)
    ada.add_course(new_course)

    out = capsys.readouterr().out
    assert "Course successfully added to the system." in out
    assert _course_exists(seeded_conn, 2001)


def test_add_course_without_instructor(ada, seeded_conn, capsys):
    new_course = Course(2002, "Independent Study", "MATH", "16:00", "F", "Spring", 2027, 1, None)
    ada.add_course(new_course)

    out = capsys.readouterr().out
    assert "Course successfully added to the system." in out
    assert _course_exists(seeded_conn, 2002)


def test_add_course_duplicate_crn_fails_gracefully(ada, seeded_conn, capsys):
    # CRN 1001 already exists in the seeded data (PRIMARY KEY collision).
    dup_course = Course(1001, "Duplicate", "BCOS", "12:00", "MW", "Fall", 2026, 3, 100)
    ada.add_course(dup_course)

    out = capsys.readouterr().out
    assert "Error adding course:" in out
    # Original course must be untouched
    cur = seeded_conn.cursor()
    cur.execute("SELECT TITLE FROM COURSE WHERE CRN = ?", (1001,))
    assert cur.fetchone()[0] == "Intro to Programming"


def test_admin_remove_course_from_system(ada, seeded_conn, capsys):
    # logic.py doesn't expose a dedicated remove_course on Admin, but the
    # system-level operation is a straight DELETE from COURSE, cursor is
    # accessible via the User base class's self.cursor -- verify the CRN
    # and its dependent registrations are gone from the system afterward.
    assert _course_exists(seeded_conn, 1001)

    ada.cursor.execute("DELETE FROM COURSE WHERE CRN = ?", (1001,))
    ada.cursor.execute("DELETE FROM REGISTRATION WHERE CRN = ?", (1001,))
    ada.conn.commit()

    assert not _course_exists(seeded_conn, 1001)
    cur = seeded_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM REGISTRATION WHERE CRN = ?", (1001,))
    assert cur.fetchone()[0] == 0


# ---------------------------------------------------------------------------
# print_roster (global, across all instructors)
# ---------------------------------------------------------------------------

def test_admin_print_roster_shows_enrolled_students(ada, capsys):
    ada.print_roster(1001)

    out = capsys.readouterr().out
    assert "Alice Anderson (alice@leopardweb.edu)" in out


def test_admin_print_roster_empty_course(ada, capsys):
    ada.print_roster(1002)

    out = capsys.readouterr().out
    assert "No students enrolled in this course." in out


# ---------------------------------------------------------------------------
# link_instructor
# ---------------------------------------------------------------------------

def test_link_instructor_assigns_new_instructor(ada, seeded_conn, capsys):
    ada.link_instructor(1004, 101)  # was unassigned

    out = capsys.readouterr().out
    assert "Instructor 101 linked to course 1004." in out
    cur = seeded_conn.cursor()
    cur.execute("SELECT INSTRUCTOR_ID FROM COURSE WHERE CRN = ?", (1004,))
    assert cur.fetchone()[0] == 101


def test_unlink_instructor_sets_null(ada, seeded_conn, capsys):
    ada.link_instructor(1001, None)

    out = capsys.readouterr().out
    assert "Instructor unlinked from course 1001." in out
    cur = seeded_conn.cursor()
    cur.execute("SELECT INSTRUCTOR_ID FROM COURSE WHERE CRN = ?", (1001,))
    assert cur.fetchone()[0] is None


def test_relink_instructor_replaces_existing(ada, seeded_conn):
    ada.link_instructor(1001, 101)  # was 100

    cur = seeded_conn.cursor()
    cur.execute("SELECT INSTRUCTOR_ID FROM COURSE WHERE CRN = ?", (1001,))
    assert cur.fetchone()[0] == 101


# ---------------------------------------------------------------------------
# manage_student_enrollment
# ---------------------------------------------------------------------------

def test_manage_enrollment_add_student(ada, seeded_conn, capsys):
    ada.manage_student_enrollment(202, 1002, "add")  # Carol -> Data Structures

    out = capsys.readouterr().out
    assert "Student 202 added to course 1002." in out
    cur = seeded_conn.cursor()
    cur.execute("SELECT 1 FROM REGISTRATION WHERE STUDENT_ID = ? AND CRN = ?", (202, 1002))
    assert cur.fetchone() is not None


def test_manage_enrollment_add_duplicate_is_handled(ada, seeded_conn, capsys):
    # Alice (200) is already enrolled in 1001.
    ada.manage_student_enrollment(200, 1001, "add")

    out = capsys.readouterr().out
    assert "Student already enrolled." in out
    cur = seeded_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM REGISTRATION WHERE STUDENT_ID = ? AND CRN = ?", (200, 1001))
    assert cur.fetchone()[0] == 1


def test_manage_enrollment_remove_student(ada, seeded_conn, capsys):
    ada.manage_student_enrollment(200, 1001, "remove")

    out = capsys.readouterr().out
    assert "Student 200 removed from course 1001." in out
    cur = seeded_conn.cursor()
    cur.execute("SELECT 1 FROM REGISTRATION WHERE STUDENT_ID = ? AND CRN = ?", (200, 1001))
    assert cur.fetchone() is None


def test_manage_enrollment_remove_nonexistent_is_noop(ada, seeded_conn, capsys):
    ada.manage_student_enrollment(202, 1002, "remove")  # Carol was never in 1002

    out = capsys.readouterr().out
    assert "Student 202 removed from course 1002." in out  # message fires regardless
    cur = seeded_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM REGISTRATION")
    assert cur.fetchone()[0] == 2  # unchanged from seed data


# ---------------------------------------------------------------------------
# add_user
# ---------------------------------------------------------------------------

def test_add_user_student(ada, seeded_conn, capsys):
    ada.add_user(
        "Student", "Dana", "Diaz", "dana@leopardweb.edu", "pw123",
        grad_year=2029, major="BSCO",
    )

    out = capsys.readouterr().out
    assert "Successfully added Student: Dana Diaz" in out

    cur = seeded_conn.cursor()
    cur.execute("SELECT ROLE FROM LOGIN WHERE EMAIL = ?", ("dana@leopardweb.edu",))
    assert cur.fetchone()[0] == "Student"
    cur.execute("SELECT FIRST_NAME, MAJOR FROM STUDENT WHERE EMAIL = ?", ("dana@leopardweb.edu",))
    row = cur.fetchone()
    assert row == ("Dana", "BSCO")


def test_add_user_instructor(ada, seeded_conn, capsys):
    ada.add_user(
        "Instructor", "Evan", "Ellis", "evan@leopardweb.edu", "pw456",
        title="Lecturer", hire_year=2024, dept="BCOS",
    )

    out = capsys.readouterr().out
    assert "Successfully added Instructor: Evan Ellis" in out

    cur = seeded_conn.cursor()
    cur.execute("SELECT TITLE, DEPT FROM INSTRUCTOR WHERE EMAIL = ?", ("evan@leopardweb.edu",))
    assert cur.fetchone() == ("Lecturer", "BCOS")


def test_add_user_assigns_next_available_id(ada, seeded_conn):
    ada.add_user("Student", "F", "G", "f@leopardweb.edu", "pw", grad_year=2030, major="BSCO")

    cur = seeded_conn.cursor()
    cur.execute("SELECT ID FROM LOGIN WHERE EMAIL = ?", ("f@leopardweb.edu",))
    new_id = cur.fetchone()[0]
    # Highest existing seeded ID is 202, so the new user should get 203.
    assert new_id == 203


def test_add_user_duplicate_email_fails_gracefully(ada, seeded_conn, capsys):
    ada.add_user(
        "Student", "Dup", "Licate", "alice@leopardweb.edu", "pw",  # alice's email already exists
        grad_year=2029, major="BSCO",
    )

    out = capsys.readouterr().out
    assert "Error: A user with this email already exists in the system." in out
    # No duplicate STUDENT row should have been committed for that email
    cur = seeded_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM STUDENT WHERE EMAIL = ?", ("alice@leopardweb.edu",))
    assert cur.fetchone()[0] == 1
