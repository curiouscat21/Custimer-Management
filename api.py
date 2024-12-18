from flask import Flask, make_response, jsonify, request, abort
from flask_mysqldb import MySQL
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)
app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "CustomerManagementSystem"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
app.config["JWT_SECRET_KEY"] = "Drew's_secret_key123"
jwt = JWTManager(app)

mysql = MySQL(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data

# Utility function for input validation
def validate_actor_data(data):
    if not data.get("first_name") or not data.get("last_name"):
        raise BadRequest("Both first_name and last_name are required.")


@app.route("/permission_levels", methods=["GET"])
def get_permission_levels():
    try:
        data = data_fetch("SELECT * FROM permission_Levels")
        return make_response(jsonify(data), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/permission_levels", methods=["POST"])
def add_permission_level():
    try:
        cur = mysql.connection.cursor()
        data = request.get_json()

        # Validate required fields
        if not data.get("Permission_Level_Code") or not data.get("Permission_Level_Description"):
            return make_response(jsonify({"error": "Both Permission_Level_Code and Permission_Level_Description are required."}), 400)

        # Check if the Permission_Level_Code already exists
        cur.execute("SELECT * FROM permission_Levels WHERE Permission_Level_Code = %s", (data["Permission_Level_Code"],))
        if cur.fetchone():
            return make_response(jsonify({"error": "Permission_Level_Code already exists."}), 400)

        # Insert data into the database
        query = """
            INSERT INTO permission_Levels (Permission_Level_Code, Permission_Level_Description)
            VALUES (%s, %s)
        """
        values = (data["Permission_Level_Code"], data["Permission_Level_Description"])
        cur.execute(query, values)

        mysql.connection.commit()
        return make_response(jsonify({"message": "Permission level(s) added successfully"}), 201)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/permission_levels/<int:id>", methods=["PUT"])
def update_permission_level(id):
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

        # Extract and validate data
        permission_description = info.get("Permission_Level_Description")  # Ensure this matches
        if not permission_description:
            return make_response(jsonify({"error": "Permission description is required"}), 400)

        # Update database
        cur.execute(
            "UPDATE permission_Levels SET Permission_Level_Description = %s WHERE Permission_Level_ID = %s",
            (permission_description, id),
        )
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Permission level not found"}), 404)

        return make_response(jsonify({"message": "Permission level updated successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/permission_levels/<int:id>", methods=["DELETE"])
def delete_permission_level(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM permission_Levels WHERE Permission_Level_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Permission level not found"}), 404)

        return make_response(jsonify({"message": "Permission level deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/people", methods=["GET"])
def get_people():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT Person_ID, Permission_Level_Code, Login_Name, 
                   Password, Personal_Details, Other_Details, Country_Name, 
                   Role_Description
            FROM people
        """)
        people = cur.fetchall()
        return make_response(jsonify({"people": people}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


# Request validation schema
class UserSchema(Schema):
    Permission_Level_Code = fields.Str(required=True)
    Login_Name = fields.Str(required=True)
    Password = fields.Str(required=True)
    Personal_Details = fields.Str(required=True)
    Other_Details = fields.Str(required=True)
    Country_Name = fields.Str(required=True)
    Role_Description = fields.Str(required=True)

@app.route("/people", methods=["POST"])
def add_person():
    try:
        info = request.get_json()
        # Validate incoming request data
        UserSchema().load(info) 

        cur = mysql.connection.cursor()
        # Extract all fields from JSON
        required_fields = [
            "Permission_Level_Code",
            "Login_Name",
            "Password",
            "Personal_Details",
            "Other_Details",
            "Country_Name",
            "Role_Description"
        ]
        
        # Validate required fields
        for field in required_fields:
            if field not in info:
                return make_response(
                    jsonify({"error": f"Missing required field: {field}"}),
                    400
                )

        # Insert data into the database
        cur.execute(
            """
            INSERT INTO people (
                Permission_Level_Code, Login_Name, Password,
                Personal_Details, Other_Details, Country_Name, Role_Description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                info["Permission_Level_Code"],
                info["Login_Name"],
                info["Password"],
                info["Personal_Details"],
                info["Other_Details"],
                info["Country_Name"],
                info["Role_Description"]
            )
        )
        mysql.connection.commit()
        return make_response(jsonify({"message": "Person added successfully"}), 201)
    except ValidationError as err:
        return make_response(jsonify({"error": err.messages}), 400)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/people/<int:id>", methods=["PUT"])
def update_person(id):
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

        # Extract all fields from JSON
        fields = {
            "Permission_Level_Code": info.get("Permission_Level_Code"),
            "Login_Name": info.get("Login_Name"),
            "Password": info.get("Password"),
            "Personal_Details": info.get("Personal_Details"),
            "Other_Details": info.get("Other_Details"),
            "Country_Name": info.get("Country_Name"),
            "Role_Description": info.get("Role_Description")
        }

        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        for key, value in fields.items():
            if value is not None:
                update_fields.append(f"{key} = %s")
                values.append(value)

        if not update_fields:
            return make_response(jsonify({"error": "No fields to update"}), 400)

        # Add the ID to the values list
        values.append(id)

        # Create and execute update query
        query = f"""
            UPDATE people 
            SET {", ".join(update_fields)}
            WHERE Person_ID = %s
        """
        cur.execute(query, values)
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Person not found"}), 404)

        return make_response(jsonify({"message": "Person updated successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/people/<int:id>", methods=["DELETE"])
def delete_person(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM people WHERE Person_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Person not found"}), 404)

        return make_response(jsonify({"message": "Person deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/internal_messages", methods=["GET"])
def get_internal_messages():
    try:
        data = data_fetch("SELECT * FROM internal_Messages")
        return make_response(jsonify(data), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/internal_messages", methods=["POST"])
def add_internal_message():
    try:
        cur = mysql.connection.cursor()
        data = request.get_json()

        # Debugging output
        print(f"Received data: {data}")

        # Check if the data is a list (for bulk insertion) or a single object
        if isinstance(data, list):
            query = """
                INSERT INTO internal_Messages (msg_from_person_id, msg_to_person_id, date_message_sent, message_subject, message_text)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = [(msg["msg_from_person_id"], msg["msg_to_person_id"], msg["date_message_sent"], 
                       msg["message_subject"], msg["message_text"]) 
                      for msg in data]
            cur.executemany(query, values)
        else:
            query = """
                INSERT INTO internal_Messages (msg_from_person_id, msg_to_person_id, date_message_sent, message_subject, message_text)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (data["msg_from_person_id"], data["msg_to_person_id"], data["date_message_sent"], 
                      data["message_subject"], data["message_text"])
            cur.execute(query, values)

        mysql.connection.commit()
        return make_response(jsonify({"message": "Internal message(s) added successfully"}), 201)
    except Exception as e:
        # Debugging output
        print(f"Error: {str(e)}")
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/internal_messages/<int:id>", methods=["PUT"])
def update_internal_message(id):
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

        # Extract and validate data
        message_content = info.get("message_content")
        sender = info.get("sender")
        recipient = info.get("recipient")
        date_sent = info.get("date_sent")
        
        if not message_content or not sender or not recipient or not date_sent:
            return make_response(jsonify({"error": "Message content, sender, recipient, and date sent are required"}), 400)

        # Update database
        cur.execute(
            "UPDATE internal_Messages SET Message_Content = %s, Sender = %s, Recipient = %s, Date_Sent = %s WHERE Message_ID = %s",
            (message_content, sender, recipient, date_sent, id),
        )
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Internal message not found"}), 404)

        return make_response(jsonify({"message": "Internal message updated successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/internal_messages/<int:id>", methods=["DELETE"])
def delete_internal_message(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM internal_Messages WHERE Message_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Internal message not found"}), 404)

        return make_response(jsonify({"message": "Internal message deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

        
@app.route("/payments", methods=["POST"])
def add_payment():
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

        # Extract and validate data
        amount = info.get("amount")
        payment_date = info.get("payment_date")
        payment_method = info.get("payment_method")
        
        if not amount or not payment_date or not payment_method:
            return make_response(jsonify({"error": "Amount, payment date, and payment method are required"}), 400)

        # Insert into database
        cur.execute(
            "INSERT INTO payments (Amount, Payment_Date, Payment_Method) VALUES (%s, %s, %s)",
            (amount, payment_date, payment_method),
        )
        mysql.connection.commit()

        return make_response(jsonify({"message": "Payment added successfully"}), 201)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/payments/<int:id>", methods=["PUT"])
def update_payment(id):
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

        # Extract and validate data
        amount = info.get("amount")
        payment_date = info.get("payment_date")
        payment_method = info.get("payment_method")
        
        if not amount or not payment_date or not payment_method:
            return make_response(jsonify({"error": "Amount, payment date, and payment method are required"}), 400)

        # Update database
        cur.execute(
            "UPDATE payments SET Amount = %s, Payment_Date = %s, Payment_Method = %s WHERE Payment_ID = %s",
            (amount, payment_date, payment_method, id),
        )
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Payment not found"}), 404)

        return make_response(jsonify({"message": "Payment updated successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/payments/<int:id>", methods=["DELETE"])
def delete_payment(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM payments WHERE Payment_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Payment not found"}), 404)

        return make_response(jsonify({"message": "Payment deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/payments", methods=["GET"])
def get_payments():
    try:
        data = data_fetch("SELECT * FROM payments")
        return make_response(jsonify(data), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/monthly_reports", methods=["GET"])
def get_monthly_reports():
    try:
        data = data_fetch("SELECT * FROM monthly_Reports")
        return make_response(jsonify(data), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    
@app.route("/monthly_reports", methods=["POST"])
def add_monthly_report():
    try:
        cur = mysql.connection.cursor()
        data = request.get_json()

        # Check if the data is a list (for bulk insertion) or a single object
        if isinstance(data, list):
            query = """
                INSERT INTO monthly_Reports (Person_ID, Date_Report_Sent, Report_Text)
                VALUES (%s, %s, %s)
            """
            values = [(report["Person_ID"], report["Date_Report_Sent"], report["Report_Text"]) 
                      for report in data]
            cur.executemany(query, values)
        else:
            query = """
                INSERT INTO monthly_Reports (Person_ID, Date_Report_Sent, Report_Text)
                VALUES (%s, %s, %s)
            """
            values = (data["Person_ID"], data["Date_Report_Sent"], data["Report_Text"])
            cur.execute(query, values)

        mysql.connection.commit()
        return make_response(jsonify({"message": "Monthly report(s) added successfully"}), 201)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/monthly_reports/<int:id>", methods=["PUT"])
def update_monthly_report(id):
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

        # Extract and validate data
        report_title = info.get("report_title")
        report_date = info.get("report_date")
        report_content = info.get("report_content")
        
        if not report_title or not report_date or not report_content:
            return make_response(jsonify({"error": "Report title, report date, and report content are required"}), 400)

        # Update database
        cur.execute(
            "UPDATE monthly_Reports SET Report_Title = %s, Report_Date = %s, Report_Content = %s WHERE Report_ID = %s",
            (report_title, report_date, report_content, id),
        )
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Monthly report not found"}), 404)

        return make_response(jsonify({"message": "Monthly report updated successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/monthly_reports/<int:id>", methods=["DELETE"])
def delete_monthly_report(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM monthly_Reports WHERE Report_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Monthly report not found"}), 404)

        return make_response(jsonify({"message": "Monthly report deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)

# User login route
@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    # Check for missing fields
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description="Missing username or password")

    username = data['username']
    password = data['password']

    # Fetch user from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM people WHERE Login_Name = %s", (username,))
    user = cur.fetchone()
    cur.close()

    # Validate user credentials
    if user is None or user['Password'] != password:  # Assuming user['Password'] is the hashed password
        abort(401, description="Invalid credentials")

    # Create JWT token (identity should be a simple value like username)
    access_token = create_access_token(identity=username)  # Pass only username as identity
    return jsonify(access_token=access_token), 200

# Role-based access control decorator
def role_required(role):
    def wrapper(fn):
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()  # This is the username (string)
            
            # Fetch the user's role from the database using the username
            cur = mysql.connection.cursor()
            cur.execute("SELECT Role_Description FROM people WHERE Login_Name = %s", (current_user,))
            user = cur.fetchone()
            cur.close()

            if user:
                role_description = user.get('Role_Description', None)
                if role_description != role:
                    return make_response(jsonify({"error": "Access forbidden: insufficient permissions"}), 403)
            else:
                return make_response(jsonify({"error": "User not found"}), 404)

            return fn(*args, **kwargs)
        return decorated_function
    return wrapper


# Admin route
@app.route("/admin", methods=["GET"])
@role_required("Manager Role")
def admin_route():
    current_user = get_jwt_identity()  # This is the username (string)
    
    # Fetch the user's role from the database using the username
    cur = mysql.connection.cursor()
    cur.execute("SELECT Role_Description FROM people WHERE Login_Name = %s", (current_user,))
    user = cur.fetchone()
    cur.close()

    if user:
        role_description = user.get('Role_Description', None)
        if role_description != "Manager Role":
            return make_response(jsonify({"error": "Access forbidden: insufficient permissions"}), 403)
    else:
        return make_response(jsonify({"error": "User not found"}), 404)

    return make_response(jsonify({"message": "Welcome to the admin panel!"}), 200)

if __name__ == "__main__":
    app.run(debug=True)
