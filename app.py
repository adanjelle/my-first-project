
from flask import Flask, request, jsonify
from datetime import date, datetime, timezone

app = Flask(__name__)

# Sample project and user records
projects = [105]
users = [24]

# Store created tasks temporarily
tasks = []

# Demo authentication token
ACCESS_TOKEN = "demo-token-123"


@app.route("/api/v1/projects/<int:project_id>/tasks", methods=["POST"])
def create_task(project_id):

    # Check authentication
    token = request.headers.get("Authorization")

    if token != f"Bearer {ACCESS_TOKEN}":
        return jsonify({
            "success": False,
            "message": "Unauthorized"
        }), 401

    # Check project
    if project_id not in projects:
        return jsonify({
            "success": False,
            "message": "Project not found"
        }), 404

    # Check JSON format
    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Content-Type must be application/json"
        }), 415

    data = request.get_json()

    # Required fields
    required = [
        "title",
        "assigneeId",
        "dueDate",
        "priority"
    ]

    missing = [
        field for field in required
        if field not in data
    ]

    if missing:
        return jsonify({
            "success": False,
            "message": "Missing required fields",
            "fields": missing
        }), 422

    # Validate title
    if not isinstance(data["title"], str) or not data["title"].strip() or len(data["title"]) > 200:
        return jsonify({
            "success": False,
            "message": "Title must contain 1 to 200 characters"
        }), 422

    # Validate assignee
    if type(data["assigneeId"]) is not int or data["assigneeId"] not in users:
        return jsonify({
            "success": False,
            "message": "Invalid assignee"
        }), 404

    # Validate priority
    if data["priority"] not in ["low", "medium", "high"]:
        return jsonify({
            "success": False,
            "message": "Priority must be low, medium or high"
        }), 422

    # Validate due date
    try:
        due_date = date.fromisoformat(data["dueDate"])
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Due date must use YYYY-MM-DD format"
        }), 422

    if due_date < date.today():
        return jsonify({
            "success": False,
            "message": "Due date cannot be in the past"
        }), 422

    # Validate optional description
    description = data.get("description")

    if description is not None and not isinstance(description, str):
        return jsonify({
            "success": False,
            "message": "Description must be text"
        }), 422

    # Create task
    task = {
        "id": len(tasks) + 501,
        "projectId": project_id,
        "title": data["title"].strip(),
        "description": description,
        "assigneeId": data["assigneeId"],
        "dueDate": due_date.isoformat(),
        "priority": data["priority"],
        "status": "pending",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }

    tasks.append(task)

    return jsonify({
        "success": True,
        "message": "Task created successfully.",
        "data": task
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
