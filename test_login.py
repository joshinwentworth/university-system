"""
Tests for login / logout behavior (all user roles).

login() lives in main.py and reads two inputs (email, password), looks the
user up in LOGIN, and returns the correct hydrated object (Student /
Instructor / Admin) plus their role string. Logout is exercised via the
menu functions, which loop until the "logout" choice is entered and then
simply return -- so we verify the loop terminates and no further action
is taken.
"""
import builtins

import pytest

from main import login, student_menu, instructor_menu, admin_menu
from logic import Student, Instructor, Admin


def _patch_inputs(monkeypatch, values):
    it = iter(values)
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(it))


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_login_student_success(seeded_conn, monkeypatch):
    _patch_inputs(monkeypatch, ["alice@leopardweb.edu", "studpass"])
    user, role = login(seeded_conn)

    assert role == "Student"
    assert isinstance(user, Student)
    assert user.user_id == 200
    assert user.first_name == "Alice"
    assert user.last_name == "Anderson"
    assert user.grad_year == 2027
    assert user.major == "BSCO"


def test_login_instructor_success(seeded_conn, monkeypatch):
    _patch_inputs(monkeypatch, ["prof.smith@leopardweb.edu", "instpass"])
    user, role = login(seeded_conn)

    assert role == "Instructor"
    assert isinstance(user, Instructor)
    assert user.user_id == 100
    assert user.dept == "BCOS"
    assert user.title == "Professor"


def test_login_admin_success(seeded_conn, monkeypatch):
    _patch_inputs(monkeypatch, ["admin@leopardweb.edu", "adminpass"])
    user, role = login(seeded_conn)

    assert role == "Admin"
    assert isinstance(user, Admin)
    assert user.user_id == 1
    assert user.office == "Room 101"


def test_login_invalid_email(seeded_conn, monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["ghost@leopardweb.edu", "whatever"])
    user, role = login(seeded_conn)

    assert user is None
    assert role is None
    assert "Invalid credentials." in capsys.readouterr().out


def test_login_wrong_password(seeded_conn, monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["alice@leopardweb.edu", "wrongpassword"])
    user, role = login(seeded_conn)

    assert user is None
    assert role is None
    assert "Invalid credentials." in capsys.readouterr().out


def test_login_email_case_or_whitespace_is_not_normalized(seeded_conn, monkeypatch):
    # Documents current (strict, case-sensitive / non-trimmed) matching behavior.
    _patch_inputs(monkeypatch, ["ALICE@leopardweb.edu", "studpass"])
    user, role = login(seeded_conn)

    assert user is None
    assert role is None


# ---------------------------------------------------------------------------
# Logout (menu loop termination)
# ---------------------------------------------------------------------------

def test_student_logout_exits_menu_without_further_action(seeded_conn, monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["alice@leopardweb.edu", "studpass"])
    student, _ = login(seeded_conn)

    _patch_inputs(monkeypatch, ["6"])  # student logout option
    student_menu(student)  # should return (loop breaks) instead of hanging

    assert "Logging out..." in capsys.readouterr().out


def test_instructor_logout_exits_menu(seeded_conn, monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["prof.smith@leopardweb.edu", "instpass"])
    instructor, _ = login(seeded_conn)

    _patch_inputs(monkeypatch, ["6"])  # instructor logout option
    instructor_menu(instructor)

    assert "Logging out..." in capsys.readouterr().out


def test_admin_logout_exits_menu(seeded_conn, monkeypatch, capsys):
    _patch_inputs(monkeypatch, ["admin@leopardweb.edu", "adminpass"])
    admin, _ = login(seeded_conn)

    _patch_inputs(monkeypatch, ["8"])  # admin logout option
    admin_menu(admin)

    assert "Logging out..." in capsys.readouterr().out

    print(0)
