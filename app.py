import os
import csv
import warnings
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pdfplumber
import pandas as pd
import requests
from urllib.parse import urlparse
import re
import logging
from flask_mail import Mail, Message

warnings.filterwarnings("ignore", category=DeprecationWarning)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management
app.logger.setLevel(logging.DEBUG)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'nandanaboba@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'mbxk fgod ldyu horf'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'nandanaboba@gmail.com'  # Default sender email
mail = Mail(app)

# Constants
PDF_FILE = "All_deals_word.pdf"  # Your PDF file path
CSV_FILE = "deals_data.csv"  # Output CSV file to store deals
USER_CSV_FILE = "users.csv"  # CSV file to store user credentials
LOGO_DIR = os.path.join(app.root_path, 'static/logos')
if not os.path.exists(LOGO_DIR):
    os.makedirs(LOGO_DIR)

# Step 1: Extract data from PDF and save to CSV
def extract_pdf_to_csv(PDF_FILE, CSV_FILE):
    data = []

    with pdfplumber.open(PDF_FILE) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            pattern = r"Add this (.+?) deal which expires on (\d{2}/\d{2}/\d{2}).*?(\d+%)"
            matches = re.findall(pattern, text)

            for match in matches:
                company_name, expire_date, offer_percentage = match
                print(f"Parsed: {company_name}, {offer_percentage}, {expire_date}")  # Debug
                data.append({
                    "Company": company_name.strip(),
                    "Offer": offer_percentage.strip(),
                    "Expire Date": expire_date.strip(),
                })

    deals_df = pd.DataFrame(data)
    # Remove spaces and '%', then convert to integer
    deals_df["Offer"] = deals_df["Offer"].str.strip().str.replace("%", "").astype(int)
    deals_df.to_csv(CSV_FILE, index=False)

# Step 2: Fetch logo dynamically (using Clearbit for now)
def fetch_logo(company_name):
    try:
        company_name = re.sub(r"[ ']", "", company_name)
        # Remove content after dots (e.g., .com)
        company_name = re.split(r"\.", company_name)[0]
        search_url = f"https://logo.clearbit.com/{company_name}.com"
        response = requests.get(search_url)
        if response.status_code == 200:
            logo_name = f"{company_name}.png"
            logo_path = os.path.join(LOGO_DIR, logo_name)
            with open(logo_path, "wb") as f:
                f.write(response.content)
            return f"/static/logos/{logo_name}"
    except Exception as e:
        print(f"Failed to fetch logo for {company_name}: {e}")
    return "/static/logos/default_logo.png"

# Step 3: Load CSV data into a list of dictionaries
def load_csv_data(csv_path):
    try:
        data = pd.read_csv(csv_path)
        if data.empty:
            print("CSV is empty.")
            return []
    except pd.errors.EmptyDataError:
        print("Error: CSV file is empty. Please check PDF extraction.")
        return []

    deals = []
    for _, row in data.iterrows():
        logo_url = fetch_logo(row["Company"])
        cleaned_name = clean_company_name(row["Company"])
        deals.append({
            "Company": row["Company"],
            "Offer": row["Offer"],
            "Expire Date": row["Expire Date"],
            "Logo": logo_url,
            "CleanName": cleaned_name,
        })
    return deals

def clean_company_name(company_name):
    company_name = re.sub(r"[ ']", "", company_name)  # Remove spaces and quotes
    company_name = re.split(r"\.", company_name)[0]  # Remove content after a dot (like .com)
    company_name = company_name.strip().lower()  # Convert to lowercase and remove any surrounding spaces
    return company_name.lower()

# Step 4: User Authentication Functions
def save_user_to_csv(firstname, lastname, username, password):
    with open(USER_CSV_FILE, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([firstname, lastname, username, password])

def authenticate_user(username, password):
    if not os.path.exists(USER_CSV_FILE):
        return False
    with open(USER_CSV_FILE, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[2] == username and row[3] == password:
                return True
    return False

def authenticate_user1(username):
    if not os.path.exists(USER_CSV_FILE):
        return False
    with open(USER_CSV_FILE, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[2] == username:
                return True
    return False

def is_valid_email(email):
    return email.endswith('@gmail.com')

def is_valid_password(password):
    if len(password) < 6:
        return False
    if not re.search(r'[A-Z]', password):  # Check for uppercase
        return False
    if not re.search(r'[a-z]', password):  # Check for lowercase
        return False
    if not re.search(r'[0-9]', password):  # Check for number
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Check for special char
        return False
    return True

def send_confirmation_email(user_email):
    subject = "Welcome to Our Service!"
    message = f"Hello, \n\nThank you for signing up with our service. We're excited to have you on board!"

    # Set up the email message
    msg = Message(subject, recipients=[user_email])
    msg.body = message

    # Send the email
    try:
        mail.send(msg)
        flash("Sign-up successful! A welcome email has been sent.", "success")
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        print("Error sending email:", e)

# Step 5: Flask Routes
@app.route("/", methods=["GET"])
def index():
    extract_pdf_to_csv(PDF_FILE, CSV_FILE)
   
    data = load_csv_data(CSV_FILE)
    search_company = request.args.get("company", "").strip()

    # Filter data by company name if search input exists
    if search_company:
        data = [deal for deal in data if search_company.lower() in deal["Company"].lower()]
    no_results = len(data) == 0

    return render_template("index.html", deals=data, search_company=search_company, no_results=no_results)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if authenticate_user(username, password):
            session["username"] = username
            session['logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for("index"))
            #flash("Sign-up successful! A welcome email has been sent.", "success")
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for('login'))
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["username"]
        password = request.form["password"]
        if authenticate_user1(email):
            flash("you already have an account")
        elif not is_valid_email(email):
            flash("Invalid email. Email must end with '@gmail.com'", "danger")
        elif not is_valid_password(password):
            flash("Invalid password. Password must contain at least 6 characters, 1 number, 1 uppercase letter, 1 lowercase letter, and 1 special character.", "danger")
        else:
            save_user_to_csv(firstname, lastname, email, password)
            flash("Signup successful! You can now log in.", "success")
            send_confirmation_email(email)
            #flash("Sign-up successful! A welcome email has been sent.", "success")
            return redirect(url_for("login"))
    
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    session['logged_in'] = False
    flash("You have logged out.", "success")
    return redirect(url_for("index"))

'''@app.route("/company/<company_name>")
def company_details(company_name):
    data = load_csv_data(CSV_FILE)
    company_deal = next((deal for deal in data if deal["Company"].lower() == company_name.lower()), None)

    if company_deal:
        return render_template("company_details.html", deal=company_deal)
    else:
        return "Company not found", 404'''

if __name__ == "__main__":
    app.run(debug=True)
