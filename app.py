import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.permanent_session_lifetime = timedelta(days=7)
bcrypt = Bcrypt(app)

# Database / Storage Setup
USE_MONGODB = True
MONGO_URI = "your_mongodb_connection_string_here"

if MONGO_URI:
    try:
        from pymongo import MongoClient
        from bson.objectid import ObjectId
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.server_info()
        db = client["task_management"]
        users_col = db["users"]
        tasks_col = db["tasks"]
        USE_MONGODB = True
        print("Connected to MongoDB Atlas")
    except Exception as e:
        print(f"MongoDB connection failed: {e}. Falling back to local storage.")

if not USE_MONGODB:
    DATA_FILE = "data.json"
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"users": [], "tasks": []}, f)

    def get_data():
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_data(data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get("_id") or user_data.get("id"))
        self.name = user_data.get("name")
        self.email = user_data.get("email")
        self.created_at = user_data.get("created_at")
        self.profile_pic = user_data.get("profile_pic")
        self.dark_mode = user_data.get('dark_mode', False)
        self.email_notifications = user_data.get('email_notifications', True)
        self.theme = user_data.get('theme', 'light')

@login_manager.user_loader
def load_user(user_id):
    if USE_MONGODB:
        from bson.objectid import ObjectId
        user_data = users_col.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
    else:
        data = get_data()
        for user in data["users"]:
            if user["id"] == user_id:
                return User(user)
    return None

# Routes
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        from datetime import datetime

        if not name or not email or not password:
            flash("All fields are required", "error")
            return redirect(url_for("signup"))

        if USE_MONGODB:
            if users_col.find_one({"email": email}):
                flash("User already exists", "error")
                return redirect(url_for("signup"))
            
            hashed_pw = generate_password_hash(password)
            users_col.insert_one({
                "name": name,
                "email": email,
                "password": hashed_pw,
                "created_at": datetime.utcnow(),
                "email_notifications": True,
                "dark_mode": False
            })
        else:
            data = get_data()
            if any(u["email"] == email for u in data["users"]):
                flash("User already exists", "error")
                return redirect(url_for("signup"))
            
            hashed_pw = generate_password_hash(password)
            new_user = {
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "password": hashed_pw,
                "created_at": datetime.utcnow().isoformat(),
                "email_notifications": True,
                "dark_mode": False
            }
            data["users"].append(new_user)
            save_data(data)

        flash("Account created. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = None
        if USE_MONGODB:
            user = users_col.find_one({"email": email})
        else:
            data = get_data()
            user = next((u for u in data["users"] if u["email"] == email), None)

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password", "error")
            return redirect(url_for("login"))

        user_obj = User(user)
        login_user(user_obj)
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_tasks = []
    if USE_MONGODB:
        from bson.objectid import ObjectId
        user_tasks = list(tasks_col.find({"user_id": ObjectId(current_user.id)}))
        for task in user_tasks:
            task["_id"] = str(task["_id"])
    else:
        data = get_data()
        user_tasks = [t for t in data["tasks"] if t["user_id"] == current_user.id]

    return render_template("dashboard.html", user=current_user, tasks=user_tasks)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    name = request.form.get("name")
    email = request.form.get("email")
    
    if not name or not email:
        flash("Name and email are required", "error")
        return redirect(url_for("profile"))

    if USE_MONGODB:
        from bson.objectid import ObjectId
        users_col.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"name": name, "email": email}}
        )
    else:
        data = get_data()
        for user in data["users"]:
            if user["id"] == current_user.id:
                user["name"] = name
                user["email"] = email
                break
        save_data(data)
    
    flash("Profile updated successfully", "success")
    return redirect(url_for("profile"))

@app.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    
    user_data = None
    if USE_MONGODB:
        from bson.objectid import ObjectId
        user_data = users_col.find_one({"_id": ObjectId(current_user.id)})
    else:
        data = get_data()
        user_data = next((u for u in data["users"] if u["id"] == current_user.id), None)

    if not user_data or not check_password_hash(user_data["password"], old_password):
        flash("Incorrect current password", "error")
        return redirect(url_for("profile"))

    hashed_pw = generate_password_hash(new_password)
    if USE_MONGODB:
        users_col.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"password": hashed_pw}}
        )
    else:
        data = get_data()
        for user in data["users"]:
            if user["id"] == current_user.id:
                user["password"] = hashed_pw
                break
        save_data(data)

    flash("Password changed successfully", "success")
    return redirect(url_for("profile"))

@app.route("/profile/upload-pic", methods=["POST"])
@login_required
def upload_profile_pic():
    flash("Profile picture upload feature is coming soon!", "info")
    return redirect(url_for("profile"))

# ======== SINGLE /settings ROUTE (REMOVE DUPLICATE) ========
@app.route("/settings")
@login_required
def settings():
    """Show settings page with current user settings"""
    try:
        # Fetch current user data with settings
        if USE_MONGODB:
            from bson.objectid import ObjectId
            user_data = users_col.find_one({"_id": ObjectId(current_user.id)})
        else:
            data = get_data()
            user_data = next((u for u in data["users"] if u["id"] == current_user.id), None)
        
        if user_data:
            # Create a user object with all settings
            user_obj = User(user_data)
            return render_template("settings.html", user=user_obj)
        else:
            flash("User data not found", "error")
            return redirect(url_for("dashboard"))
            
    except Exception as e:
        print(f"Error loading settings: {e}")
        flash("Error loading settings", "error")
        return redirect(url_for("dashboard"))

@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title")
    description = request.form.get("description", "")
    if not title:
        return redirect(url_for("dashboard"))

    if USE_MONGODB:
        from bson.objectid import ObjectId
        tasks_col.insert_one({
            "title": title,
            "description": description,
            "status": "Pending",
            "user_id": ObjectId(current_user.id)
        })
    else:
        data = get_data()
        new_task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "status": "Pending",
            "user_id": current_user.id
        }
        data["tasks"].append(new_task)
        save_data(data)

    return redirect(url_for("dashboard"))

@app.route("/tasks/<task_id>/done")
@login_required
def complete_task(task_id):
    if USE_MONGODB:
        from bson.objectid import ObjectId
        tasks_col.update_one(
            {"_id": ObjectId(task_id), "user_id": ObjectId(current_user.id)},
            {"$set": {"status": "Completed"}}
        )
    else:
        data = get_data()
        for task in data["tasks"]:
            if (task.get("id") == task_id or str(task.get("_id")) == task_id) and task["user_id"] == current_user.id:
                task["status"] = "Completed"
                break
        save_data(data)
    return redirect(url_for("dashboard"))

@app.route("/tasks/<task_id>/edit", methods=["POST"])
@login_required
def edit_task(task_id):
    new_title = request.form.get("title")
    new_description = request.form.get("description", "")
    if not new_title:
        return redirect(url_for("dashboard"))

    if USE_MONGODB:
        from bson.objectid import ObjectId
        tasks_col.update_one(
            {"_id": ObjectId(task_id), "user_id": ObjectId(current_user.id)},
            {"$set": {"title": new_title, "description": new_description, "status": "Pending"}}
        )
    else:
        data = get_data()
        for task in data["tasks"]:
            if (task.get("id") == task_id or str(task.get("_id")) == task_id) and task["user_id"] == current_user.id:
                task["title"] = new_title
                task["description"] = new_description
                task["status"] = "Pending"
                break
        save_data(data)
    
    flash("Task updated successfully", "success")
    return redirect(url_for("dashboard"))

@app.route("/tasks/<task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    if USE_MONGODB:
        from bson.objectid import ObjectId
        tasks_col.delete_one({"_id": ObjectId(task_id), "user_id": ObjectId(current_user.id)})
    else:
        data = get_data()
        data["tasks"] = [task for task in data["tasks"] if not (task.get("id") == task_id or str(task.get("_id")) == task_id) or task["user_id"] != current_user.id]
        save_data(data)
    flash("Task deleted successfully", "success")
    return redirect(url_for("dashboard"))

# ======== UPDATED SETTINGS ENDPOINTS ========
@app.route("/settings/update", methods=["POST"])
@login_required
def update_settings():
    """Update user settings via AJAX"""
    try:
        # Parse JSON data
        if not request.is_json:
            return jsonify({"success": False, "error": "Invalid content type"}), 400
            
        data = request.get_json()
        
        if USE_MONGODB:
            from bson.objectid import ObjectId
            update_data = {}
            
            # Handle email notifications
            if 'email_notifications' in data:
                # Convert to boolean safely
                email_val = data['email_notifications']
                if isinstance(email_val, str):
                    email_val = email_val.lower() == 'true'
                update_data['email_notifications'] = bool(email_val)
            
            # Handle dark mode
            if 'dark_mode' in data:
                # Convert to boolean safely
                dark_val = data['dark_mode']
                if isinstance(dark_val, str):
                    dark_val = dark_val.lower() == 'true'
                update_data['dark_mode'] = bool(dark_val)
            
            if update_data:
                result = users_col.update_one(
                    {"_id": ObjectId(current_user.id)},
                    {"$set": update_data}
                )
                return jsonify({
                    "success": True, 
                    "message": "Settings updated",
                    "data": update_data
                })
            else:
                return jsonify({"success": False, "error": "No valid settings provided"}), 400
                
        else:
            # Local storage implementation
            data_file = get_data()
            updated = False
            
            for user in data_file["users"]:
                if user["id"] == current_user.id:
                    if 'email_notifications' in data:
                        email_val = data['email_notifications']
                        if isinstance(email_val, str):
                            email_val = email_val.lower() == 'true'
                        user['email_notifications'] = bool(email_val)
                        updated = True
                    
                    if 'dark_mode' in data:
                        dark_val = data['dark_mode']
                        if isinstance(dark_val, str):
                            dark_val = dark_val.lower() == 'true'
                        user['dark_mode'] = bool(dark_val)
                        updated = True
                    
                    break
            
            if updated:
                save_data(data_file)
                return jsonify({"success": True, "message": "Settings updated"})
            else:
                return jsonify({"success": False, "error": "No changes made"}), 400
                
    except Exception as e:
        print(f"Error in update_settings: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    try:
        if USE_MONGODB:
            from bson.objectid import ObjectId
            # Delete user's tasks first
            tasks_col.delete_many({"user_id": ObjectId(current_user.id)})
            # Delete the user
            users_col.delete_one({"_id": ObjectId(current_user.id)})
        else:
            data = get_data()
            # Remove user's tasks
            data["tasks"] = [task for task in data["tasks"] if task["user_id"] != current_user.id]
            # Remove the user
            data["users"] = [user for user in data["users"] if user["id"] != current_user.id]
            save_data(data)
        
        logout_user()
        flash("Your account has been deleted successfully.", "success")
        return redirect(url_for("login"))
    except Exception as e:
        flash(f"Error deleting account: {str(e)}", "error")
        return redirect(url_for("settings"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
