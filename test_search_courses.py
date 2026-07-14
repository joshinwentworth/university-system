"""
Tests for course searching -- both the no-argument ("search all") form and
the keyword-parameterized form -- across all three roles. search_courses()
is defined once on the base User class, so Student/Instructor/Admin share
identical behavior; we parametrize across all three to prove that.
"""
import pytest

from logic import Student, Instructor, Admin, Course


@pytest.fixture(params=["student", "instructor", "admin"])
def any_user(request, seeded_conn):
    if request.param == "student":
        return Student(seeded_conn, 200, "Alice", "Anderson", "alice@leopardweb.edu", 2027, "BSCO")
    elif request.param == "instructor":
        return Instructor(seeded_conn, 100, "John", "Smith", "prof.smith@leopardweb.edu", "Professor", 2010, "BCOS")
    else:
        return Admin(seeded_conn, 1, "Ada", "Admin", "admin@leopardweb.edu", "Registrar", "Room 101")


def test_search_all_courses_returns_every_course(any_user):
    results = any_user.search_courses()
    crns = {c.crn for c in results}

    assert len(results) == 4
    assert crns == {1001, 1002, 1003, 1004}
    assert all(isinstance(c, Course) for c in results)


def test_search_courses_by_department(any_user):
    results = any_user.search_courses("MATH")

    assert len(results) == 1
    assert results[0].crn == 1003
    assert results[0].dept == "MATH"


def test_search_courses_by_title_keyword(any_user):
    results = any_user.search_courses("Data")

    assert len(results) == 1
    assert results[0].title == "Data Structures"


def test_search_courses_is_case_and_substring_insensitive_via_like(any_user):
    # SQL LIKE with %param% is case-insensitive for ASCII in SQLite by default.
    results = any_user.search_courses("intro")

    assert len(results) == 1
    assert results[0].crn == 1001


def test_search_courses_no_match_returns_empty_list(any_user):
    results = any_user.search_courses("Nonexistent Subject")

    assert results == []


def test_search_courses_partial_dept_matches_all_bcos(any_user):
    results = any_user.search_courses("BCOS")
    crns = {c.crn for c in results}

    # 3 BCOS courses seeded (1001, 1002, 1004)
    assert crns == {1001, 1002, 1004}
