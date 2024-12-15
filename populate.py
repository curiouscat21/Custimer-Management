from flask import Flask
from flask_mysqldb import MySQL
from faker import Faker
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "CustomerManagementSystem"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
fake = Faker()

# Function to generate fake people data
def generate_people():
    # Fetch all country names and role names
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Country_Name FROM Countries")
    country_names = [row['Country_Name'] for row in cursor.fetchall()]

    cursor.execute("SELECT Role_Name FROM Roles")
    role_names = [row['Role_Name'] for row in cursor.fetchall()]

    cursor.close()

    people = []
    for _ in range(25):  # Generate 25 people
        country_name = random.choice(country_names)  # Randomly select a country name
        role_name = random.choice(role_names)  # Randomly select a role name
        login_name = fake.user_name()  # Faker generates a random username
        password = fake.password(length=12)  # Faker generates a random password
        personal_details = fake.text(max_nb_chars=200)  # Faker generates random personal details
        other_details = fake.text(max_nb_chars=200)  # Faker generates random other details

        person = (country_name, role_name, login_name, password, personal_details, other_details)
        people.append(person)

    return people


def generate_permission_levels():
    permission_levels = [
        ('ADM', 'Administrator'),
        ('USR', 'User'),
        ('MOD', 'Moderator'),
        ('MGR', 'Manager'),
        ('DEV', 'Developer'),
        ('SUP', 'Support'),
        ('HR', 'Human Resources'),
        ('FIN', 'Finance'),
        ('MK', 'Marketing'),
        ('OPS', 'Operations'),
        ('ENG', 'Engineer'),
        ('SA', 'Sales'),
        ('IT', 'IT Specialist'),
        ('PM', 'Project Manager'),
        ('TL', 'Team Leader'),
        ('ACCT', 'Accountant'),
        ('DES', 'Designer'),
        ('QAS', 'Quality Assurance Specialist'),
        ('CS', 'Customer Service'),
        ('BD', 'Business Development'),
        ('COO', 'Chief Operating Officer'),
        ('CFO', 'Chief Financial Officer'),
        ('CEO', 'Chief Executive Officer'),
        ('CTO', 'Chief Technology Officer'),
        ('CIO', 'Chief Information Officer')
    ]
    return permission_levels

def generate_internal_messages():
    # Get all existing Person_IDs
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Person_ID FROM People")
    person_ids = [row['Person_ID'] for row in cursor.fetchall()]
    cursor.close()

    messages = []
    for _ in range(50):  # Generate 50 messages
        msg_from_person_id = random.choice(person_ids)
        msg_to_person_id = random.choice(person_ids)
        
        # Ensure the sender and receiver are not the same person
        while msg_from_person_id == msg_to_person_id:
            msg_to_person_id = random.choice(person_ids)

        date_message_sent = fake.date_this_year() + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
        message_subject = fake.sentence(nb_words=6)
        message_text = fake.text(max_nb_chars=500)  # Faker generates random message text

        message = (msg_from_person_id, msg_to_person_id, date_message_sent, message_subject, message_text)
        messages.append(message)

    return messages

# Function to insert internal messages data into the database
def insert_data():
    db_connection = mysql.connection
    cursor = db_connection.cursor()

    # Insert Internal Messages
    messages = generate_internal_messages()
    for message in messages:
        try:
            cursor.execute("""
                INSERT INTO Internal_Messages (Msg_From_Person_ID, Msg_To_Person_ID, Date_Message_Sent, Message_Subject, Message_Text)
                VALUES (%s, %s, %s, %s, %s)
            """, message)
        except mysql.connection.IntegrityError as e:
            print(f"Error inserting message: {e}")

    # Commit the transaction
    db_connection.commit()
    cursor.close()

def generate_payments():
    # Get all existing Person_IDs
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Person_ID FROM People")
    person_ids = [row['Person_ID'] for row in cursor.fetchall()]
    cursor.close()

    payments = []
    for _ in range(50):  # Generate 50 payments
        person_id = random.choice(person_ids)
        amount_due = round(random.uniform(50, 1000), 2)  # Random amount between 50 and 1000
        reminder_sent_yn = random.choice(['Y', 'N'])
        
        if reminder_sent_yn == 'Y':
            # Generate a random date for when the reminder was sent
            date_reminder_sent = fake.date_this_year() + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            # Generate a random date for when the payment was made (can be after the reminder date)
            date_paid = date_reminder_sent + timedelta(days=random.randint(0, 30))  # Payment made within 30 days
        else:
            date_reminder_sent = None
            date_paid = None
        
        other_details = fake.text(max_nb_chars=200)  # Random text for other details

        payment = (person_id, amount_due, reminder_sent_yn, date_reminder_sent, date_paid, other_details)
        payments.append(payment)

    return payments

# Function to insert payments data into the database
def insert_data():
    db_connection = mysql.connection
    cursor = db_connection.cursor()

    # Insert Payments
    payments = generate_payments()
    for payment in payments:
        try:
            cursor.execute("""
                INSERT INTO Payments (Person_ID, Amount_Due, Reminder_Sent_YN, Date_Reminder_Sent, Date_Paid, Other_Details)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, payment)
        except mysql.connection.IntegrityError as e:
            print(f"Error inserting payment: {e}")

    # Commit the transaction
    db_connection.commit()
    cursor.close()

def generate_monthly_reports():
    # Get all existing Person_IDs
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Person_ID FROM People")
    person_ids = [row['Person_ID'] for row in cursor.fetchall()]
    cursor.close()

    reports = []
    for _ in range(50):  # Generate 50 reports
        person_id = random.choice(person_ids)
        # Generate a random date for when the report was sent (within the current year)
        date_report_sent = fake.date_this_year() + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
        report_text = fake.text(max_nb_chars=500)  # Random text for the report

        report = (person_id, date_report_sent, report_text)
        reports.append(report)

    return reports

# Function to insert monthly reports data into the database
def insert_data():
    db_connection = mysql.connection
    cursor = db_connection.cursor()

    # Insert Monthly Reports
    reports = generate_monthly_reports()
    for report in reports:
        try:
            cursor.execute("""
                INSERT INTO Monthly_Reports (Person_ID, Date_Report_Sent, Report_Text)
                VALUES (%s, %s, %s)
            """, report)
        except mysql.connection.IntegrityError as e:
            print(f"Error inserting report: {e}")

    # Commit the transaction
    db_connection.commit()
    cursor.close()

# Route to trigger data generation
@app.route('/generate_data')
def generate_data():
    insert_data()
    return "Fake monthly reports data inserted successfully!"

if __name__ == "__main__":
    app.run(debug=True)