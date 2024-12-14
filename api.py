from flask import Flask, make_response, jsonify, request
from flask_mysqldb import MySQL
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.config["MYSQL_HOST"] = "127.0.0.1"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "CustomerManagementSystem"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

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
        data = data_fetch("SELECT * FROM Permission_Levels")
        return make_response(jsonify(data), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/permission_levels", methods=["POST"])
def add_permission_level():
    try:
        cur = mysql.connection.cursor()
        data = request.get_json()

        # Debugging output
        print(f"Received data: {data}")

        # Check if the data is a list (for bulk insertion) or a single object
        if isinstance(data, list):
            query = """
                INSERT INTO Permission_Levels (Permission_Level_Code, Permission_Level_Description)
                VALUES (%s, %s)
            """
            values = [(level["Permission_Level_Code"], level["Permission_Level_Description"]) for level in data]
            cur.executemany(query, values)
        else:
            query = """
                INSERT INTO Permission_Levels (Permission_Level_Code, Permission_Level_Description)
                VALUES (%s, %s)
            """
            values = (data["Permission_Level_Code"], data["Permission_Level_Description"])
            cur.execute(query, values)

        mysql.connection.commit()
        return make_response(jsonify({"message": "Permission level(s) added successfully"}), 201)
    except Exception as e:
        # Debugging output
        print(f"Error: {str(e)}")
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/permission_levels/<int:id>", methods=["PUT"])
def update_permission_level(id):
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

        # Extract and validate data
        permission_description = info.get("permission_description")
        if not permission_description:
            return make_response(jsonify({"error": "Permission description is required"}), 400)

        # Update database
        cur.execute(
            "UPDATE Permission_Levels SET Permission_Description = %s WHERE Permission_Level_ID = %s",
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
        cur.execute("DELETE FROM Permission_Levels WHERE Permission_Level_ID = %s", (id,))
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
            FROM People
        """)
        people = cur.fetchall()
        return make_response(jsonify({"people": people}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/people", methods=["POST"])
def add_person():
    try:
        cur = mysql.connection.cursor()
        info = request.get_json()

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
            INSERT INTO People (
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
            UPDATE People 
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
        cur.execute("DELETE FROM People WHERE Person_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Person not found"}), 404)

        return make_response(jsonify({"message": "Person deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)


@app.route("/internal_messages", methods=["GET"])
def get_internal_messages():
    try:
        data = data_fetch("SELECT * FROM Internal_Messages")
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
                INSERT INTO Internal_Messages (msg_from_person_id, msg_to_person_id, date_message_sent, message_subject, message_text)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = [(msg["msg_from_person_id"], msg["msg_to_person_id"], msg["date_message_sent"], 
                       msg["message_subject"], msg["message_text"]) 
                      for msg in data]
            cur.executemany(query, values)
        else:
            query = """
                INSERT INTO Internal_Messages (msg_from_person_id, msg_to_person_id, date_message_sent, message_subject, message_text)
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
            "UPDATE Internal_Messages SET Message_Content = %s, Sender = %s, Recipient = %s, Date_Sent = %s WHERE Message_ID = %s",
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
        cur.execute("DELETE FROM Internal_Messages WHERE Message_ID = %s", (id,))
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
            "INSERT INTO Payments (Amount, Payment_Date, Payment_Method) VALUES (%s, %s, %s)",
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
            "UPDATE Payments SET Amount = %s, Payment_Date = %s, Payment_Method = %s WHERE Payment_ID = %s",
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
        cur.execute("DELETE FROM Payments WHERE Payment_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Payment not found"}), 404)

        return make_response(jsonify({"message": "Payment deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route("/payments", methods=["GET"])
def get_payments():
    try:
        data = data_fetch("SELECT * FROM Payments")
        return make_response(jsonify(data), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route("/monthly_reports", methods=["GET"])
def get_monthly_reports():
    try:
        data = data_fetch("SELECT * FROM Monthly_Reports")
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
                INSERT INTO Monthly_Reports (Person_ID, Date_Report_Sent, Report_Text)
                VALUES (%s, %s, %s)
            """
            values = [(report["Person_ID"], report["Date_Report_Sent"], report["Report_Text"]) 
                      for report in data]
            cur.executemany(query, values)
        else:
            query = """
                INSERT INTO Monthly_Reports (Person_ID, Date_Report_Sent, Report_Text)
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
            "UPDATE Monthly_Reports SET Report_Title = %s, Report_Date = %s, Report_Content = %s WHERE Report_ID = %s",
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
        cur.execute("DELETE FROM Monthly_Reports WHERE Report_ID = %s", (id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return make_response(jsonify({"error": "Monthly report not found"}), 404)

        return make_response(jsonify({"message": "Monthly report deleted successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)



if __name__ == "__main__":
    app.run(debug=True)
