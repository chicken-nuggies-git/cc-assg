from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import boto3
from config import *
from botocore import UNSIGNED
from botocore.client import Config
import time


app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = mysql.connector.connect(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'employee'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')

@app.route("/student")
def student():
    return render_template('student.html')

#route to company page
@app.route("/company")
def company():
    return render_template('company.html')

# Route to admin login page
@app.route("/adminLogin")
def adminLogin(msg=""):
    return render_template('adminLogin.html', msg=msg)

# Route to admin profile page
@app.route("/adminProfile/<admin_id>")
def adminProfile(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get admin data from database
        cursor.execute('SELECT * FROM admin WHERE id = %s', (admin_id,))
        account = cursor.fetchone() # If account not exists, account = None
    finally:
        cursor.close()

    print(account[0])

    return render_template('adminProfile.html', admin_id=admin_id, account=account)

# Route to company list page
@app.route("/admin/<admin_id>/companyList", methods=['GET'])
def companyList(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get all company data from database
        cursor.execute('SELECT * FROM company')
        companies = cursor.fetchall()
    finally:
        cursor.close()

    print(companies)

    return render_template('companyList.html', companies=companies, admin_id=admin_id)

# Route to supervisor list page
@app.route("/admin/<admin_id>/supervisorList", methods=['GET'])
def supervisorList(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get all supervisor data from database
        cursor.execute('SELECT * FROM supervisor')
        supervisors = cursor.fetchall()
    finally:
        cursor.close()

    return render_template('supervisorList.html', supervisors=supervisors, admin_id=admin_id)

# Route to add supervisor page
@app.route("/admin/<admin_id>/addSupervisor", methods=['GET'])
def addSupervisor(admin_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Get last supervisor id from database
        cursor.execute('SELECT id FROM supervisor ORDER BY id DESC LIMIT 1')
        last_supervisor_id = cursor.fetchone()
    finally:
        cursor.close()

    # Change tuple to integer
    last_supervisor_id = int(last_supervisor_id[0])

    # Increment last supervisor id by 1
    new_supervisor_id = last_supervisor_id + 1

    # Change integer back to six character string
    new_supervisor_id = str(new_supervisor_id).zfill(6)

    return render_template('addSupervisor.html', admin_id=admin_id, new_supervisor_id=new_supervisor_id)

# Admin edit profile function
@app.route("/editProfile/<admin_id>")
def editProfile(admin_id):
    # Get user input name, email and phone number from HTML form
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')

    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update admin data in database
        cursor.execute('UPDATE admin SET name = %s, email = %s, phone_number = %s WHERE id = %s', (name, email, phone, admin_id))
        db_conn.commit()
    finally:
        cursor.close()

    return redirect(url_for('adminProfile', admin_id=admin_id))

# Admin login function
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Get user input email and password from HTML form
    admin_id = request.args.get('admin_id')
    password = request.args.get('password')

    # Connect to MySQL database
    cursor = db_conn.cursor()
    
    try:
        # Check if email exists in accounts table in out database
        cursor.execute('SELECT * FROM admin WHERE id = %s', (admin_id,))
        account = cursor.fetchone() # If account not exists, account = None
    finally:
        cursor.close()

    # If account exists in accounts table in out database
    if account:
        # Check if password correct
        if password == account[4]:
            # If password correct, redirect to admin page
            return redirect(url_for('adminProfile', admin_id=admin_id))
        else:
            # If password incorrect, redirect to admin login page with error message
            msg = 'Account exists but password incorrect'
            return render_template('adminLogin.html', msg=msg)
    # If account not exists in accounts table in out database
    else:
        msg = 'Account does not exists'
        return render_template('adminLogin.html', msg=msg)
    
# Admin logout function
@app.route("/adminLogout")
def adminLogout():
    return redirect(url_for('adminLogin'))

# Admin accept company function
@app.route("/<admin_id>/acceptCompany/<company_id>")
def acceptCompany(admin_id, company_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update company status in database
        cursor.execute('UPDATE company SET status = %s, isReviewed = 1 WHERE id = %s', ('ACCEPTED', company_id))
        db_conn.commit()

        # Get all company data from database
        cursor.execute('SELECT * FROM company')
        companies = cursor.fetchall()
    finally:
        cursor.close()

    return redirect(url_for('companyList', admin_id=admin_id))

# Admin reject company function
@app.route("/<admin_id>/rejectCompany/<company_id>")
def rejectCompany(admin_id, company_id):
    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Update company status in database
        cursor.execute('UPDATE company SET status = %s, isReviewed = 1 WHERE id = %s', ('REJECTED', company_id))
        db_conn.commit()

        # Get all company data from database
        cursor.execute('SELECT * FROM company')
        companies = cursor.fetchall()
    finally:
        cursor.close()

    return redirect(url_for('companyList', admin_id=admin_id))

# Admin add supervisor function
@app.route("/addSupervisor/<admin_id>/<supervisor_id>", methods=['GET', 'POST'])
def addSupervisorFunc(admin_id, supervisor_id):
    # Get user input name, email, phone number and password from HTML form
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    password = request.args.get('password')

    print(supervisor_id)

    # Connect to MySQL database
    cursor = db_conn.cursor()

    try:
        # Insert supervisor data into database
        cursor.execute('INSERT INTO supervisor VALUES (%s, %s, %s, %s, %s)', (supervisor_id, password, name, email, phone))
        db_conn.commit()

        print('Supervisor added successfully')

        # Get all supervisor data from database
        cursor.execute('SELECT * FROM supervisor')
        supervisors = cursor.fetchall()
    finally:
        cursor.close()

    return redirect(url_for('supervisorList', admin_id=admin_id))

@app.route("/xy")
def xyPortfolio():
    return render_template('xy-portfolio.html')

@app.route("/kelvin")
def kelvinPortfolio():
    return render_template('kelvin-portfolio.html')

@app.route("/kh")
def khPortfolio():
    return render_template('kh-portfolio.html')

@app.route("/jt")
def jtPortfolio():
    return render_template('jt-portfolio.html')

@app.route("/yk")
def ykPortfolio():
    return render_template('yk-portfolio.html')

# upload folder
# Create an S3 client with unsigned configuration (anonymous)
s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route('/uploadResume', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    # Assuming student_id is stored in session after login
    student_id = "1001"
    
    if not student_id:
        return "User not logged in", 403
    
    cursor = db_conn.cursor()
    try:
        # Retrieve the old resume URL from the database
        cursor.execute('SELECT resume FROM student WHERE student_id = %s', (student_id,))
        result = cursor.fetchone()
        old_s3_url = result[0] if result else None
    finally:
        cursor.close()
    
    # Upload the new file to S3
    s3_key = f"resumes/{student_id}/{file.filename}"
    s3_client.upload_fileobj(file, 'cheahkaihui-bucket', s3_key)
    
    # Update the resume column in the student table with correct column name
    s3_url = f"https://{custombucket}.s3.{customregion}.amazonaws.com/{s3_key}"
    
    cursor = db_conn.cursor()
    try:
        cursor.execute('UPDATE student SET resume = %s WHERE student_id = %s', (s3_url, student_id))
        db_conn.commit()
    finally:
        cursor.close()
    
    # Delete the old file from S3 if it exists
    if old_s3_url:
        print("Old S3 URL:", old_s3_url)
        old_s3_key = old_s3_url.split(f"https://{custombucket}.s3.{customregion}.amazonaws.com/")[1]
        print("Old S3 Key:", old_s3_key)
        s3_client.delete_object(Bucket='cheahkaihui-bucket', Key=old_s3_key)

    return "File uploaded, database updated, and old file deleted successfully"

#for uploading progress report 
@app.route('/uploadProgressReport', methods=['POST'])
def upload_file1():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    # Assuming student_id is stored in session after login
    student_id = "1001"
    
    if not student_id:
        return "User not logged in", 403
    
    # Upload the file to S3
    #test for now
    s3_key = f"progressReport/{student_id}/{file.filename}"
    s3_client.upload_fileobj(file, 'cheahkaihui-bucket', s3_key)
    
    # Update the resume column in the student table
    s3_url = f"https://{custombucket}.s3.{customregion}.amazonaws.com/{s3_key}"
    
    cursor = db_conn.cursor()
    try:
        cursor.execute('UPDATE student SET progress_report = %s WHERE student_id = %s', (s3_url, student_id))
        db_conn.commit()
    finally:
        cursor.close()

    return "File uploaded and database updated successfully"

#check if got the correct extension or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)