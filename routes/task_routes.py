import re

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models.models import Task

from extensions import db

task = Blueprint("task", __name__)

# =========================
# TITLE VALIDATION
# =========================

def validate_title(title):

    # Remove extra spaces

    title = title.strip()

    # Minimum / Maximum length

    if len(title) < 3 or len(title) > 100:
        return False

    # Prevent only numbers

    if title.isdigit():
        return False

    return True

# =========================
# DESCRIPTION VALIDATION
# =========================

def validate_description(description):

    description = description.strip()

    # Minimum length

    if len(description) < 5:
        return False

    # Maximum length

    if len(description) > 500:
        return False

    return True

# =========================
# DASHBOARD
# =========================

@task.route("/dashboard")
@login_required
def dashboard():

    search = request.args.get("search", "")

    # SEARCH TASKS

    if search:

        tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.title.ilike(f"%{search}%")
        ).all()

    else:

        tasks = Task.query.filter_by(
            user_id=current_user.id
        ).all()

    # TASK COUNTS

    completed = Task.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).count()

    pending = Task.query.filter_by(
        user_id=current_user.id,
        status="Pending"
    ).count()

    progress = Task.query.filter_by(
        user_id=current_user.id,
        status="In Progress"
    ).count()

    total_tasks = Task.query.filter_by(
        user_id=current_user.id
    ).count()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        completed=completed,
        pending=pending,
        progress=progress,
        total_tasks=total_tasks
    )

# =========================
# CREATE TASK
# =========================

@task.route("/create", methods=["GET", "POST"])
@login_required
def create_task():

    if request.method == "POST":

        title = request.form.get("title").strip()

        description = request.form.get(
            "description"
        ).strip()

        status = request.form.get("status")

        # EMPTY FIELD VALIDATION

        if not title or not description:

            flash(
                "All fields are required",
                "danger"
            )

            return redirect(
                url_for("task.create_task")
            )

        # TITLE VALIDATION

        if not validate_title(title):

            flash(
                "Title must be 3-100 characters and not only numbers",
                "danger"
            )

            return redirect(
                url_for("task.create_task")
            )

        # DESCRIPTION VALIDATION

        if not validate_description(description):

            flash(
                "Description must be between 5 and 500 characters",
                "danger"
            )

            return redirect(
                url_for("task.create_task")
            )

        # STATUS VALIDATION

        valid_status = [
            "Pending",
            "In Progress",
            "Completed"
        ]

        if status not in valid_status:

            flash(
                "Invalid status selected",
                "danger"
            )

            return redirect(
                url_for("task.create_task")
            )

        # CREATE TASK

        new_task = Task(
            title=title,
            description=description,
            status=status,
            user_id=current_user.id
        )

        db.session.add(new_task)

        db.session.commit()

        flash(
            "Task created successfully",
            "success"
        )

        return redirect(
            url_for("task.dashboard")
        )

    return render_template("create_task.html")

# =========================
# EDIT TASK
# =========================

@task.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_task(id):

    task_data = Task.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":

        title = request.form.get("title").strip()

        description = request.form.get(
            "description"
        ).strip()

        status = request.form.get("status")

        # EMPTY FIELD VALIDATION

        if not title or not description:

            flash(
                "Fields cannot be empty",
                "danger"
            )

            return redirect(
                url_for("task.edit_task", id=id)
            )

        # TITLE VALIDATION

        if not validate_title(title):

            flash(
                "Title must be 3-100 characters and not only numbers",
                "danger"
            )

            return redirect(
                url_for("task.edit_task", id=id)
            )

        # DESCRIPTION VALIDATION

        if not validate_description(description):

            flash(
                "Description must be between 5 and 500 characters",
                "danger"
            )

            return redirect(
                url_for("task.edit_task", id=id)
            )

        # STATUS VALIDATION

        valid_status = [
            "Pending",
            "In Progress",
            "Completed"
        ]

        if status not in valid_status:

            flash(
                "Invalid status selected",
                "danger"
            )

            return redirect(
                url_for("task.edit_task", id=id)
            )

        # UPDATE TASK

        task_data.title = title

        task_data.description = description

        task_data.status = status

        db.session.commit()

        flash(
            "Task updated successfully",
            "success"
        )

        return redirect(
            url_for("task.dashboard")
        )

    return render_template(
        "edit_task.html",
        task=task_data
    )

# =========================
# DELETE TASK
# =========================

@task.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_task(id):

    task_data = Task.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(task_data)

    db.session.commit()

    flash(
        "Task deleted successfully",
        "success"
    )

    return redirect(
        url_for("task.dashboard")
    )