from flask import Flask, render_template, request, redirect, url_for, make_response
from review import review_code
import jwt
import datetime
from functools import wraps
import json
import os
import re

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this_in_production"

# Dummy users database
USERS = {
    "admin": "password123",
    "user": "user123",
    "dev": "dev123"
}

STATS_FILE = "stats.json"

# ===== STATS FUNCTIONS =====
def load_stats():
    """Load stats from JSON file"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {"total_lines": 2300, "total_views": 0, "reviews": []}

def save_stats(stats):
    """Save stats to JSON file"""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def add_page_view():
    """Count each page visit as 1 view"""
    stats = load_stats()
    stats["total_views"] += 1
    save_stats(stats)

def extract_score(review_text):
    """Extract numeric score from Gemini review (looks for X/10)"""
    match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', review_text)
    if match:
        try:
            return float(match.group(1))
        except:
            return None
    return None

def add_review(code, score):
    """Track code review - add to total_lines and store score"""
    stats = load_stats()
    stats["total_lines"] += len(code.split('\n'))  # Count lines, not characters
    
    if score is not None:
        stats["reviews"].append({"score": score, "timestamp": str(datetime.datetime.now())})
    
    save_stats(stats)

def get_stats():
    """Get current stats for display"""
    stats = load_stats()
    
    total_views = stats.get("total_views", 0)
    total_lines = stats.get("total_lines", 0)
    reviews = stats.get("reviews", [])
    
    # Calculate average score
    if reviews:
        avg_score = sum(r.get("score", 0) for r in reviews) / len(reviews)
        avg_score = round(avg_score, 1)
    else:
        avg_score = 0
    
    return {
        "views": total_views,
        "lines": total_lines,
        "avg_score": avg_score
    }

# ===== AUTH & ROUTES =====

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        
        if not token:
            return redirect(url_for('login'))
        
        try:
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            current_user = data['user']
        except:
            return redirect(url_for('login'))
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        
        if username in USERS and USERS[username] == password:
            # Create JWT token
            token = jwt.encode(
                {
                    'user': username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                app.secret_key,
                algorithm="HS256"
            )
            
            response = make_response(redirect(url_for('home')))
            response.set_cookie('token', token, httponly=True)
            return response
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response

@app.route("/", methods=["GET", "POST"])
@token_required
def home(current_user):
    # Count this page visit as 1 view
    add_page_view()
    
    result = ""
    code = ""

    if request.method == "POST":
        # Get code from form data or request values
        code = request.values.get("code", "").strip()

        try:
            if code:
                result = review_code(code)
                
                # Extract score and track
                score = extract_score(result)
                add_review(code, score)
            else:
                result = "Please enter some code."
        except Exception as e:
            result = f"Error:\n\n{e}"

    # Get current stats
    stats = get_stats()

    return render_template(
        "index.html",
        code=code,
        result=result,
        username=current_user,
        total_views=stats["views"],
        total_lines="2.3K",
        avg_score=stats["avg_score"]
    )

if __name__=="__main__":
    app.run(debug=True)