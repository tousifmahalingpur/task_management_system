import re

from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    flash,
    url_for
)

from flask_login import (
    login_user,
    logout_user,
    current_user
)

from models.models import User

from extensions import db, bcrypt

auth = Blueprint("auth", __name__)

# =========================
# EMAIL VALIDATION
# =========================

def validate_email(email):

    email = email.strip().lower()

    # BASIC EMAIL FORMAT

    pattern = (
        r'^[a-zA-Z0-9._%+-]+'
        r'@[a-zA-Z0-9.-]+'
        r'\.[a-zA-Z]{2,}$'
    )

    if not re.match(pattern, email):

        return False

    # NAME PART BEFORE @

    name_part = email.split("@")[0]

    # PREVENT ONLY NUMBERS
    # Example: 222@gmail.com

    if name_part.isdigit():

        return False

    # PREVENT VERY SHORT NAMES

    if len(name_part) < 3:

        return False

    # PREVENT REPETITIVE TEXT
    # Example: aaaaa@gmail.com

    if len(set(name_part)) == 1:

        return False

    return True

# =========================
# USERNAME VALIDATION
# =========================

def validate_username(username):

    username = username.strip()

    # LENGTH CHECK

    if len(username) < 3 or len(username) > 30:

        return False

    # ONLY NUMBERS NOT ALLOWED

    if username.isdigit():

        return False

    # REPETITIVE USERNAMES
    # Example: hhhhh

    if len(set(username.lower())) == 1:

        return False

    return True

# =========================
# PASSWORD VALIDATION
# =========================

def validate_password(password):

    # MINIMUM LENGTH

    if len(password) < 6:

        return False

    # PREVENT REPETITIVE PASSWORDS
    # Example: hhhhhh

    if len(set(password.lower())) == 1:

        return False

    # REQUIRE LETTER

    has_letter = any(
        char.isalpha()
        for char in password
    )

    # REQUIRE NUMBER

    has_number = any(
        char.isdigit()
        for char in password
    )

    if not has_letter or not has_number:

        return False

    return True

# =========================
# HOME PAGE
# =========================

@auth.route("/")
def home():

    return render_template("index.html")

# =========================
# SIGNUP
# =========================

@auth.route(
    "/signup",
    methods=["GET", "POST"]
)

def signup():

    if current_user.is_authenticated:

        return redirect(
            url_for("task.dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username"
        ).strip()

        email = request.form.get(
            "email"
        ).strip().lower()

        password = request.form.get(
            "password"
        )

        confirm_password = request.form.get(
            "confirm_password"
        )

        # =========================
        # EMPTY FIELD CHECK
        # =========================

        if (
            not username or
            not email or
            not password or
            not confirm_password
        ):

            flash(
                "All fields are required",
                "danger"
            )

            return redirect(
                url_for("auth.signup")
            )

        # =========================
        # USERNAME VALIDATION
        # =========================

        if not validate_username(username):

            flash(
                "Username must be 3-30 characters and not repetitive or numeric only",
                "danger"
            )

            return redirect(
                url_for("auth.signup")
            )

        # =========================
        # EMAIL VALIDATION
        # =========================

        if not validate_email(email):

            flash(
                "Invalid or weak email address",
                "danger"
            )

            return redirect(
                url_for("auth.signup")
            )

        # =========================
        # PASSWORD VALIDATION
        # =========================

        if not validate_password(password):

            flash(
                "Password must contain letters and numbers and not repetitive",
                "danger"
            )

            return redirect(
                url_for("auth.signup")
            )

        # =========================
        # PASSWORD MATCH
        # =========================

        if password != confirm_password:

            flash(
                "Passwords do not match",
                "danger"
            )

            return redirect(
                url_for("auth.signup")
            )

        # =========================
        # EXISTING USER CHECK
        # =========================

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered",
                "danger"
            )

            return redirect(
                url_for("auth.signup")
            )

        # =========================
        # HASH PASSWORD
        # =========================

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        # =========================
        # CREATE USER
        # =========================

        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        flash(
            "Account created successfully",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template("signup.html")

# =========================
# LOGIN
# =========================

@auth.route(
    "/login",
    methods=["GET", "POST"]
)

def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("task.dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email"
        ).strip().lower()

        password = request.form.get(
            "password"
        )

        # EMPTY CHECK

        if not email or not password:

            flash(
                "All fields are required",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # FIND USER

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "User not found",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # PASSWORD CHECK

        if not bcrypt.check_password_hash(
            user.password,
            password
        ):

            flash(
                "Incorrect password",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )

        # LOGIN USER

        login_user(user)

        flash(
            "Login successful",
            "success"
        )

        return redirect(
            url_for("task.dashboard")
        )

    return render_template("login.html")

# =========================
# LOGOUT
# =========================

@auth.route("/logout")

def logout():

    logout_user()

    flash(
        "Logged out successfully",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )