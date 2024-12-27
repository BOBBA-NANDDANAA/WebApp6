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
from datetime import datetime, timedelta

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
EXCEL_FILE = "D:/imagereader/EXCEL1.xlsx"  # Your PDF file path
# Define file paths
CSV_DIR = "D:/output_csv/"  # Directory to save the daily CSV files  # Output CSV file to store deals
os.makedirs(CSV_DIR, exist_ok=True)
USER_CSV_FILE = "users.csv"  # CSV file to store user credentials
LOGO_DIR = os.path.join(app.root_path, 'static/logos')
if not os.path.exists(LOGO_DIR):
    os.makedirs(LOGO_DIR)


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


import os
from datetime import datetime, timedelta
import pandas as pd

# Define file paths


# Mapping shorthand names to full bank names
BANK_MAPPING = {
    "bof": "Bank Of America",
    "amex": "American Express",
    # Add other mappings as required
}

# Ensure CSV output directory exists


def process_excel_and_generate_csv():
    today = datetime.today()
    current_date_str = today.strftime("%d-%m-%Y")
    previous_date_str = (today - timedelta(days=1)).strftime("%d-%m-%Y")

    # Load the Excel file
    try:
        excel_data = pd.ExcelFile(EXCEL_FILE)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return

    for sheet_name in excel_data.sheet_names:
        # Parse the bank shorthand and date from the sheet name
        parts = sheet_name.split("_")
        if len(parts) != 2:
            print(f"Skipping sheet {sheet_name}, invalid naming format.")
            continue

        bank_shorthand, sheet_date = parts
        csv_file = f"{CSV_DIR}{bank_shorthand}_{current_date_str}.csv"
        previous_csv = f"{CSV_DIR}{bank_shorthand}_{previous_date_str}.csv"

        # Map the shorthand to the full bank name
        bank_name = BANK_MAPPING.get(bank_shorthand.lower(), bank_shorthand)

        # Check if the sheet corresponds to today
        if sheet_date != today.strftime("%d-%m-%Y"):
            print(f"Skipping sheet {sheet_name}, not today's date.")
            continue

        # Read the sheet and process the data
        try:
            sheet_data = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=None)
            sheet_data.columns = ["Company", "Logo URL", "Offer", "Expire Date"]  # Explicit column names

            # Check if sheet has data
            if sheet_data.empty:
                print(f"Sheet {sheet_name} is empty. Checking fallback...")
                # Fallback to the previous day's CSV
                if os.path.exists(previous_csv):
                    print(f"Using previous day's CSV: {previous_csv}")
                    os.rename(previous_csv, csv_file)
                else:
                    print(f"No data available for {bank_shorthand} on {current_date_str} or {previous_date_str}.")
                continue

            # Add Bank Name column
            sheet_data["Bank Name"] = bank_name

            # Clean "Expire Date" column
            sheet_data["Expire Date"] = sheet_data["Expire Date"].apply(parse_expiry_date)

            # Save to CSV
            sheet_data.to_csv(csv_file, index=False)
            print(f"Generated CSV: {csv_file}")

        except Exception as e:
            print(f"Error processing sheet {sheet_name}: {e}")

def parse_expiry_date(expiry_date):
    """
    Parse and clean the expiry date column to a consistent format (MM/DD/YYYY).
    """
    try:
        # Match date patterns in the text
        match = re.search(r"(\d{2}/\d{2}/\d{2,4})", str(expiry_date))
        if match:
            date_str = match.group(1)
            # Parse the date to ensure consistency
            date_obj = datetime.strptime(date_str, "%m/%d/%y") if len(date_str.split("/")[2]) == 2 else datetime.strptime(date_str, "%m/%d/%Y")
            return date_obj.strftime("%m/%d/%Y")
        else:
            # Handle relative date strings like "Expires in 5 days"
            if "Expires in" in str(expiry_date):
                days = int(re.search(r"(\d+)", str(expiry_date)).group(1))
                expiry_date = (datetime.today() + timedelta(days=days)).strftime("%m/%d/%Y")
                return expiry_date
    except Exception as e:
        print(f"Error parsing expiry date '{expiry_date}': {e}")
    return expiry_date  # Return as is if parsing fails


def load_csv_and_process_individual_banks():
    """
    Load each bank's individual CSV file generated today, process the data, and output the results.
    If today's CSV is not available, fallback to yesterday's CSV.
    """
    today = datetime.today()
    current_date_str = today.strftime("%d-%m-%Y")
    previous_date_str = (today - timedelta(days=1)).strftime("%d-%m-%Y")
    all_deals = []

    for bank_shorthand in BANK_MAPPING.keys():
        # Define the CSV file paths
        today_csv = f"{CSV_DIR}{bank_shorthand}_{current_date_str}.csv"
        yesterday_csv = f"{CSV_DIR}{bank_shorthand}_{previous_date_str}.csv"

        # Check for today's file; fallback to yesterday's if necessary
        csv_file = today_csv if os.path.exists(today_csv) else (yesterday_csv if os.path.exists(yesterday_csv) else None)

        if not csv_file:
            print(f"No data available for {bank_shorthand} on {current_date_str} or {previous_date_str}.")
            continue

        # Load and process the CSV file
        try:
            data = pd.read_csv(csv_file)
            if data.empty:
                print(f"{csv_file} is empty.")
                continue

            print(f"Processing {csv_file}...")
            deals = process_bank_csv(data, bank_shorthand)
            all_deals.extend(deals)

        except Exception as e:
            print(f"Error loading or processing {csv_file}: {e}")

    # Optional: Save consolidated data if required
    consolidated_file = f"{CSV_DIR}consolidated_deals_{current_date_str}.csv"
    if all_deals:
        pd.DataFrame(all_deals).to_csv(consolidated_file, index=False)
        print(f"Consolidated deals saved to {consolidated_file}")
    else:
        print("No deals to consolidate.")

    return all_deals

BANK_WEBSITES = {
    "Chase": "https://www.chase.com",
    "Bank Of America": "https://www.bankofamerica.com",
    "Wells Fargo": "https://www.wellsfargo.com",
    "Citibank": "https://www.citi.com",
    "PNC Bank": "https://www.pnc.com",
    "American Express": "https://www.americanexpress.com/en-us/account/login/"
    # Add more banks as needed
}

def process_bank_csv(data, bank_shorthand):
    """
    Process the CSV data for a single bank and return the processed deals.
    """
    deals = []
    bank_name = BANK_MAPPING.get(bank_shorthand.lower(), bank_shorthand)
    unwanted_phrases = ["see details", "great deals","Use Link"]
    for _, row in data.iterrows():
        try:
            company_offer = row["Offer"]
            
            # Check if the company name contains any unwanted phrases
            if any(phrase in company_offer.lower() for phrase in unwanted_phrases):
                print(f"Skipping row with unwanted phrase: {company_offer}")
                continue  # Skip this row

            cleaned_name = clean_company_name(row["Company"])
            cleaned_name1 = clean_company_name2(cleaned_name)
          #  CLEANED_OFFER = clean_offer(row["Offer"])
            deals.append({
                "Bank_Website": BANK_WEBSITES.get(bank_name, "#"),
                "Bank": bank_name,
                "Company": cleaned_name,
                "Offer": row["Offer"],
                "Expire Date": row["Expire Date"],
                "Logo": row["Logo URL"],
                "CleanName": cleaned_name1,
            })
        except Exception as e:
            print(f"Error processing row: {e}")
            continue
    return deals

def clean_company_name2(company_name):
    cleaned_string = company_name.replace(" ", "")
    company_name = re.sub(r"[^\w\s]", "", cleaned_string) 
    return company_name


#def clean_offer(offer):

def clean_company_name(company_name):
    # Step 1: Remove spaces, quotes, and unnecessary characters
    # Step 2: Remove common unwanted words (e.g., 'logo', 'company', etc.)
    unwanted_words = ["company", "logo", "inc", "corp", "co", "limited", "llc", "plc", "and", "deals", "international","select","store.","destinations"]
    pattern = r'\b(?:' + '|'.join(unwanted_words) + r')\b'
    company_name = re.sub(pattern, "", company_name, flags=re.IGNORECASE)  # Remove unwanted words

    # Step 3: Remove content after the first occurrence of a hyphen "-" or dot "."
     # If hyphen has spaces around it, treat it as separator
    company_name = company_name.split(" - ")[0]
    
    company_name2 = company_name.split(".")
    company_name = company_name2[0]
    


    # Step 4: Clean up extra spaces
    company_name = " ".join(company_name.split())  # Remove extra spaces

    company_name = re.split(r"\bsince\b", company_name, flags=re.IGNORECASE)[0]
    

    def custom_title_case(text):
        # Apply title case, but ensure "s" after an apostrophe stays lowercase
        text = text.title()
        text = re.sub(r"(\b\w+)'S", r"\1's", text)  # Fix 'S to 's (e.g., Levi's)
        return text
    
    # Step 5: Convert to proper title case
    if len(company_name) == 3:
        company_name = company_name.upper()  # Convert to uppercase
    else:
        company_name = custom_title_case(company_name)  # Title case (proper capitalization)

    company_name = re.sub(r"[^\w\s'].*", "", company_name)  # Remove everything after first special character

    # Step 3: Clean up extra spaces
    company_name = " ".join(company_name.split())  # Remove extra spaces# Step 1: Remove all non-alphanumeric characters except spaces
    #company_name = re.sub(r"[^\w\s]", "", company_name)  # Remove all non-alphanumeric characters except spaces

    return company_name





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
    process_excel_and_generate_csv()
   
    data = load_csv_and_process_individual_banks()

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
