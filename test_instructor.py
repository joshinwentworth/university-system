"""
Tests for Instructor.print_roster / Instructor.search_roster -- assembling
and printing the class list for a course an instructor teaches -- plus
print_teaching_schedule as supporting coverage.
"""
import pytest

from logic import Instructor


@pytest.fixture
def prof_smith(seeded_conn):
    # John Smith (100) teaches CRN 1001 (Alice enrolled) and 1002 (nobody enrolled)
    return Instructor(seeded_conn, 100, "John", "Smith", "prof.smith@leopardweb.edu", "Professor", 2010, "BCOS")


@pytest.fixture
def prof_jones(seeded_conn):
    # Jane Jones (101) teaches CRN 1003 (Bob enrolled)
    return Instructor(seeded_conn, 101, "Jane", "Jones", "prof.jones@leopardweb.edu", "Assistant Prof", 2018, "MATH")


# ---------------------------------------------------------------------------
# print_roster
# ---------------------------------------------------------------------------

def test_print_roster_lists_enrolled_students(prof_smith, capsys):
    prof_smith.print_roster(1001)

    out = capsys.readouterr().out
    assert "Alice Anderson (alice@leopardweb.edu)" in out


def test_print_roster_empty_course_shows_no_students_message(prof_smith, capsys):
    prof_smith.print_roster(1002)  # Data Structures has no registrations

    out = capsys.readouterr().out
    assert "No students enrolled or you do not teach this course." in out


def test_print_roster_refuses_course_taught_by_someone_else(prof_smith, capsys):
    # CRN 1003 belongs to prof_jones (101), not prof_smith (100), even
    # though Bob is enrolled in it.
    prof_smith.print_roster(1003)

    out = capsys.readouterr().out
    assert "No students enrolled or you do not teach this course." in out
    assert "Bob" not in out


def test_print_roster_other_instructor_sees_their_own_course(prof_jones, capsys):
    prof_jones.print_roster(1003)

    out = capsys.readouterr().out
    assert "Bob Baker (bob@leopardweb.edu)" in out


# ---------------------------------------------------------------------------
# search_roster
# ---------------------------------------------------------------------------

def test_search_roster_finds_matching_student_by_first_name(prof_smith, capsys):
    prof_smith.search_roster(1001, "Ali")

    out = capsys.readouterr().out
    assert "Alice Anderson (alice@leopardweb.edu)" in out


def test_search_roster_finds_matching_student_by_last_name(prof_smith, capsys):
    prof_smith.search_roster(1001, "Anderson")

    out = capsys.readouterr().out
    assert "Alice Anderson" in out


def test_search_roster_no_match_in_course(prof_smith, capsys):
    prof_smith.search_roster(1001, "Zzzznomatch")

    out = capsys.readouterr().out
    assert "No matching students found in this course." in out


def test_search_roster_scoped_to_instructor_own_course(prof_smith, capsys):
    # Bob matches "Bob" but is enrolled in CRN 1003, taught by prof_jones,
    # not prof_smith -- so prof_smith's search should find nothing.
    prof_smith.search_roster(1003, "Bob")

    out = capsys.readouterr().out
    assert "No matching students found in this course." in out


# ---------------------------------------------------------------------------
# print_teaching_schedule (supporting coverage)
# ---------------------------------------------------------------------------

def test_print_teaching_schedule_lists_assigned_courses(prof_smith, capsys):
    prof_smith.print_teaching_schedule()

    out = capsys.readouterr().out
    assert "Intro to Programming" in out
    assert "Data Structures" in out


def test_print_teaching_schedule_empty_when_unassigned(seeded_conn, capsys):
    new_instructor = Instructor(seeded_conn, 999, "No", "Body", "nobody@leopardweb.edu", "Adjunct", 2025, "BCOS")
    new_instructor.print_teaching_schedule()

    out = capsys.readouterr().out
    assert "You are not assigned to teach any courses." in out
