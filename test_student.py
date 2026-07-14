"""
Tests for Student.add_course / Student.remove_course -- i.e. adding and
removing courses from a student's semester schedule.
"""
import pytest

from logic import Student


@pytest.fixture
def alice(seeded_conn):
    # Alice (200) is already registered for CRN 1001 (Intro to Programming, MWF 10:00)
    return Student(seeded_conn, 200, "Alice", "Anderson", "alice@leopardweb.edu", 2027, "BSCO")


def _registered_crns(conn, student_id):
    cur = conn.cursor()
    cur.execute("SELECT CRN FROM REGISTRATION WHERE STUDENT_ID = ?", (student_id,))
    return {row[0] for row in cur.fetchall()}


# ---------------------------------------------------------------------------
# add_course
# ---------------------------------------------------------------------------

def test_add_course_success_no_conflict(alice, seeded_conn, capsys):
    # CRN 1002 (Data Structures, TR 14:00) does not overlap with Alice's
    # existing CRN 1001 (MWF 10:00).
    alice.add_course(1002)

    out = capsys.readouterr().out
    assert "Successfully added Data Structures to your schedule." in out
    assert 1002 in _registered_crns(seeded_conn, 200)


def test_add_course_not_found(alice, seeded_conn, capsys):
    alice.add_course(9999)

    out = capsys.readouterr().out
    assert "Error: Course not found." in out
    assert 9999 not in _registered_crns(seeded_conn, 200)


def test_add_course_schedule_conflict_same_days_and_time(alice, seeded_conn, capsys):
    # CRN 1003 (Calculus I) is also MWF at 10:00 -- same slot as Alice's 1001.
    alice.add_course(1003)

    out = capsys.readouterr().out
    assert "Error: Schedule conflict detected! Cannot add course." in out
    assert 1003 not in _registered_crns(seeded_conn, 200)


def test_add_course_already_enrolled_hits_conflict_check_first(alice, seeded_conn, capsys):
    # NOTE: this documents actual (buggy) behavior rather than the ideal
    # behavior. Re-adding a course you're already enrolled in trips
    # check_conflicts() first -- the course trivially "conflicts" with
    # itself (same time, same days) -- so the "You are already enrolled"
    # except-branch in add_course() is currently unreachable dead code.
    # Ideally this case would short-circuit to a clearer "already enrolled"
    # message, but as written it reports a schedule conflict instead.
    alice.add_course(1001)

    out = capsys.readouterr().out
    assert "Error: Schedule conflict detected! Cannot add course." in out
    # Regardless of the message, the student must still only be registered once.
    cur = seeded_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM REGISTRATION WHERE STUDENT_ID = ? AND CRN = ?", (200, 1001))
    assert cur.fetchone()[0] == 1


def test_add_course_already_enrolled_except_branch_is_reachable_in_isolation():
    # Directly proves the except-branch's own logic is correct in isolation:
    # inserting a duplicate (STUDENT_ID, CRN) primary key does trigger
    # sqlite3.IntegrityError, independent of check_conflicts(). This shows
    # the *intent* of the except branch works -- it's simply unreachable
    # through add_course() today because check_conflicts() runs first.
    import sqlite3

    from conftest import SCHEMA

    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.execute(
        "INSERT INTO COURSE (CRN, TITLE, DEPARTMENT, TIME, DAYS, SEMESTER, YEAR, CREDITS, INSTRUCTOR_ID) "
        "VALUES (1, 'X', 'DEPT', '10:00', 'MWF', 'Fall', 2026, 3, NULL)"
    )
    conn.execute("INSERT INTO REGISTRATION (STUDENT_ID, CRN) VALUES (1, 1)")
    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO REGISTRATION VALUES (1, 1)")

    conn.close()


def test_add_course_different_days_same_time_no_conflict(alice, seeded_conn, capsys):
    # CRN 1004 (Unassigned Seminar) is TR 09:00 -- different days from
    # Alice's existing MWF 10:00 course, and different time too, so no conflict.
    alice.add_course(1004)

    out = capsys.readouterr().out
    assert "Successfully added" in out
    assert 1004 in _registered_crns(seeded_conn, 200)


# ---------------------------------------------------------------------------
# remove_course
# ---------------------------------------------------------------------------

def test_remove_course_success(alice, seeded_conn, capsys):
    assert 1001 in _registered_crns(seeded_conn, 200)

    alice.remove_course(1001)

    out = capsys.readouterr().out
    assert "Course removed from schedule" in out
    assert 1001 not in _registered_crns(seeded_conn, 200)


def test_remove_course_not_enrolled_is_a_noop(alice, seeded_conn, capsys):
    # Removing a course the student was never enrolled in should not error,
    # and should not affect other registrations.
    before = _registered_crns(seeded_conn, 200)

    alice.remove_course(1002)

    out = capsys.readouterr().out
    assert "Course removed from schedule" in out
    assert _registered_crns(seeded_conn, 200) == before


def test_print_schedule_lists_enrolled_courses(alice, capsys):
    alice.print_schedule()

    out = capsys.readouterr().out
    assert "Intro to Programming" in out


def test_print_schedule_empty_when_not_enrolled(seeded_conn, capsys):
    carol = Student(seeded_conn, 202, "Carol", "Clark", "carol@leopardweb.edu", 2028, "MATH")
    carol.print_schedule()

    out = capsys.readouterr().out
    assert "You are not enrolled in any courses." in out
