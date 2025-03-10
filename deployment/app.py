from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
import bcrypt
import pandas as pd
import joblib
import scipy.sparse as sp
from sklearn.metrics.pairwise import cosine_similarity
import  pickle
import numpy as np
from sklearn.neighbors import NearestNeighbors
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__)
app.secret_key = "your_secret_key"



from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session and flash messages

# Database connection
DB_URL = "postgresql://neondb_owner:npg_p8FLyjz5NKqi@ep-tiny-brook-a8vnh9fx-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# ------------------- USER MANAGEMENT -------------------
def tokenize_tags(text):
    return text.split(",")

# Load all models
print("Loading recommendation models...")
df = pd.read_csv('models/processed_jobs.csv')
with open('models/vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)
with open('models/svd.pkl', 'rb') as f:
    svd = pickle.load(f)
with open('models/kmeans.pkl', 'rb') as f:
    kmeans = pickle.load(f)
with open('models/feature_info.pkl', 'rb') as f:
    feature_info = pickle.load(f)
job_features_reduced = np.load('models/job_features_reduced.npy')
print("Recommendation models loaded successfully")

def send_job_recommendations_email(receiver_email, recommendations):
    try:
       
        sender_email = "jasmineshaik160304@gmail.com"

        sender_password = "xzii ajlt jjtt vejd"   
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        if not receiver_email:
            print("No email address provided")
            return False

        subject = "🚨 Job Recommendations Based on Your Search 🚨"

        # Construct email body
        body = f"""JOB RECOMMENDATIONS BASED ON YOUR SEARCH
{'='*50}\n"""

        # Add job recommendations
        for i, job in enumerate(recommendations, 1):
            similarity_percent = job.get('Similarity', 0) * 100
            
            body += f"Title: {job.get('Title', 'Not specified')}\n"
            body += f"Company: {job.get('Company', 'Not specified')}\n"
            body += f"Link: {job.get('Job_Link', '#')}\n"
            body += f"{'='*50}\n"

        # Add footer
        body += """
        Thank you for using our Job Recommendation System.
        Save jobs you're interested in by clicking the "Save" button in your dashboard.

        Best of luck with your job search!
        """

        # Send email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Job recommendations email sent to {receiver_email}")
            return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":  # Ensure form submission
        email = request.form.get("email")  # Use .get() to prevent KeyError
        password = request.form.get("password")

        if not email or not password:  # Check if both fields are filled
            flash("Please fill out all fields.", "danger")
            return redirect(url_for("signup"))

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash("User already exists. Please log in.", "danger")
            return redirect(url_for("signup"))

        cur.execute("INSERT INTO users (email, password,role) VALUES (%s, %s, %s)", (email,hashed_password, "user"))
        conn.commit()
        cur.close()
        conn.close()

        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))  # Redirect to login page after signup

    return render_template("signup.html")  # Render signup page for GET request


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Please fill out all fields.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password, role FROM users WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            session["email"] = email
            session["role"] = result[1]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")  # Render login page for GET request

# Admin Login Route
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check hardcoded credentials (Modify this if using a DB)
        if username == "admin" and password == "admin123":
            session["admin"] = True
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid username or password!", "danger")

    return render_template("admin_login.html")

# Admin Dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html")

# Admin Manage Courses (Adding & Viewing)
@app.route("/admin_market_trends", methods=["GET", "POST"])
def admin_market_trends():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        course_name = request.form["course_name"]
        course_link = request.form["course_link"]
        cur.execute("INSERT INTO courses (name, link) VALUES (%s, %s)", (course_name, course_link))
        conn.commit()
        flash("Course added successfully!", "success")

    cur.execute("SELECT id, name, link FROM courses")
    courses = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("admin_market_trends.html", courses=courses)

# Admin Logout
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("admin_login"))

# User Market Trends Page (View Only)
@app.route("/market_trends")
def market_trends():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("market_trends.html", courses=courses)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))




# ------------------- JOB RECOMMENDATION SYSTEM -------------------

# def recommend_jobs(job_title, skills, section, experience, salary, locations, top_n=5):
#     """Returns top N job recommendations."""
#     job_desc = f"{job_title} in {section} with skills: {', '.join(skills)}"
#     user_text_vector = vectorizer.transform([job_desc])

#     user_numeric_vector = scaler.transform([[experience, salary]])
#     user_numeric_vector = sp.csr_matrix(user_numeric_vector)

#     location_columns = [col for col in df.columns if col.startswith("location_")]
#     user_location_vector = sp.csr_matrix((1, len(location_columns)))

#     if locations:
#         user_location_df = pd.DataFrame(0, index=[0], columns=location_columns)
#         for location in locations:
#             location_column_name = f"location_{location.lower()}"
#             if location_column_name in user_location_df.columns:
#                 user_location_df[location_column_name] = 1
#         user_location_vector = sp.csr_matrix(user_location_df.values)

#     user_vector = sp.hstack([user_text_vector, user_numeric_vector, user_location_vector])
#     similarity_scores = cosine_similarity(user_vector, final_features)
#     ranked_indices = similarity_scores.argsort()[0][::-1][:top_n]

#     return [
#         {"Company": df.iloc[i]["Company"], "Job_Link": df.iloc[i]["job_link"]}
#         for i in ranked_indices
#     ]
# Function for tokenizing


def recommend_jobs(job_title, skills, section, experience, salary, locations, top_n=5):
    """Returns top N job recommendations using the clustering-based recommendation system."""
    # Combine skills input
    if isinstance(skills, list):
        skills_input = ", ".join(skills)
    else:
        skills_input = skills
    
    # Format salary as string if it's a number
    if isinstance(salary, (int, float)):
        salary = str(salary)
    
    # Format experience as string if it's a number
    if isinstance(experience, (int, float)):
        experience = str(experience)
    
    # Get first location if multiple are provided
    location_input = locations[0].lower() if locations and isinstance(locations, list) else ""
    
    # Preprocess user input
    skills_clean = skills_input.lower().replace(", ", ",").strip()
    skills_vec = vectorizer.transform([skills_clean]).toarray()

    # Process salary
    if salary and salary.strip():
        try:
            salary_val = float(salary)
        except ValueError:
            salary_val = feature_info['salary_mean']
    else:
        salary_val = feature_info['salary_mean']
    salary_norm = salary_val / feature_info['salary_max']

    # Process experience
    if experience and experience.strip():
        try:
            exp_val = float(experience)
        except ValueError:
            exp_val = feature_info['exp_mean']
    else:
        exp_val = feature_info['exp_mean']
    exp_norm = exp_val / feature_info['exp_max']

    # Process location
    loc_clean = location_input.strip()
    loc_vec = np.array([1 if loc_clean == loc else 0 for loc in feature_info['top_locations']]).reshape(1, -1)

    # Combine features
    user_features = np.hstack((skills_vec, [[salary_norm, exp_norm]], loc_vec))
    
    # Reduce dimensions with SVD
    user_features_reduced = svd.transform(user_features)
    
    # Find user's cluster
    user_cluster = kmeans.predict(user_features_reduced)[0]
    
    # Filter jobs in user's cluster
    cluster_jobs_idx = df[df["cluster"] == user_cluster].index
    cluster_job_features = job_features_reduced[cluster_jobs_idx]
    
    # If the cluster is too small, consider all jobs
    if len(cluster_jobs_idx) < top_n:
        cluster_jobs_idx = df.index
        cluster_job_features = job_features_reduced
    
    # Use kNN to find top recommendations
    knn = NearestNeighbors(n_neighbors=min(top_n, len(cluster_jobs_idx)), metric="cosine")
    knn.fit(cluster_job_features)
    distances, indices = knn.kneighbors(user_features_reduced)
    
  
    recommended_indices = cluster_jobs_idx[indices[0]]
    
    # Calculate similarity score (1 - distance)
    similarities = 1 - distances[0]
    
    # Return formatted recommendations
    return [
        {
            "Company": df.iloc[i]["Company"],
            "Job_Link": df.iloc[i]["job_link"],
            "Title": df.iloc[i]["Title"],
            "Location": df.iloc[i]["Location"],
            "Experience": df.iloc[i]["Experience"],
            "Salary": df.iloc[i]["Salary"],
            "Similarity": float(similarities[idx])
        }
        for idx, i in enumerate(recommended_indices)
    ]
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "email" not in session:
        return redirect(url_for("home"))

    recommendations = []
    if request.method == "POST":
        job_title = request.form.get("job_title", "").strip()
        skills = request.form.get("skills", "").split(",") if request.form.get("skills") else []
        section = request.form.get("section", "").strip()
        experience = int(request.form.get("experience", 0))
        salary = int(request.form.get("salary", 0))
        locations = request.form.getlist("locations")

        recommendations = recommend_jobs(job_title, skills, section, experience, salary, locations)
        
        # Send email with recommendations if we found any
        if recommendations and len(recommendations) > 0:
            user_email = session.get("email")
            send_job_recommendations_email(user_email, recommendations)
            flash("Job recommendations have been emailed to you!", "success")

    return render_template("dashboard.html", recommendations=recommendations)


# ------------------- SAVING JOBS -------------------



from flask import flash, redirect, url_for, session, request, render_template

@app.route("/save_job", methods=["POST"])
def save_job():
    if "email" not in session:
        return redirect(url_for("home"))

    user_email = session["email"]
    company = request.form["company"]
    job_link = request.form["job_link"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Avoid duplicate job entries
    cur.execute("SELECT * FROM saved_jobs WHERE user_email = %s AND job_link = %s", (user_email, job_link))
    existing_job = cur.fetchone()

    if not existing_job:
        cur.execute(
            "INSERT INTO saved_jobs (user_email, company, job_link) VALUES (%s, %s, %s)",
            (user_email, company, job_link)
        )
        conn.commit()
        flash("Job saved successfully!", "success")  # ✅ Flash message works now
    else:
        flash("This job is already saved.", "warning")

    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))




@app.route("/saved_jobs")
def saved_jobs():
    if "email" not in session:
        return redirect(url_for("home"))

    user_email = session["email"]
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch saved jobs for the user
    cur.execute("SELECT company, job_link FROM saved_jobs WHERE user_email = %s", (user_email,))
    saved_jobs = cur.fetchall()  # Fetch all saved jobs as a list of tuples

    cur.close()
    conn.close()

    return render_template("saved_jobs.html", saved_jobs=saved_jobs)



# ------------------- RUN FLASK APP -------------------

if __name__ == "__main__":
    app.run(debug=True)
