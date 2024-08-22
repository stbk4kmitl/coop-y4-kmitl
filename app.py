from flask import Flask, request, redirect, url_for, render_template
import pandas as pd
import os
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

DATABASE_URL = "postgresql://postgres:2002@localhost:5432/Database for Project "


def delete_files_in_temp(temp_folder):
    try:
        files = os.listdir(temp_folder)
        for file in files:
            file_path = os.path.join(temp_folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Deleted All files in temp folder.")
    except OSError:
        print("Error while deleting files in temp folder.")


#def delete_tables_in_db():

def allowed_file(filename):

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def run_selected_lines_from_sql(sql_file_path, line_numbers):
    # เปิดไฟล์ .sql เพื่ออ่านบรรทัดที่ต้องการ
    with open(sql_file_path, 'r') as file:
        lines = file.readlines()
    # สร้าง SQL ที่จะรันจากบรรทัดที่เลือก
    selected_sql = ''.join([lines[i] for i in line_numbers])
    # เชื่อมต่อกับฐานข้อมูลและรัน SQL ที่เลือก
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute(selected_sql)  
        # ตรวจสอบว่า SQL ส่งผลลัพธ์หรือไม่
        if cur.description:
            result = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
        else:
            result = None
            column_names = None
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

    return result, column_names


def import_csv_to_db(csv_file_path):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    with open(csv_file_path, 'r') as f:
        #import data into table hardwarenames
        cur.copy_expert(sql.SQL("""
            COPY hardwarenames FROM STDIN WITH CSV HEADER
        """), f)
    conn.commit()
    cur.close()
    conn.close()




@app.route('/')
def index():

    temp_folder = r"D:\TELECOM\Telecom4-1\GIT for Project\coop-y4-kmitl\temp"
    delete_files_in_temp(temp_folder)

    run_selected_lines_from_sql(sql_file_path='db_tools.sql', line_numbers=[6])

    return redirect(url_for('upload_file'))




@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Convert Excel file to CSV
            csv_filename = filename.rsplit('.', 1)[0] + '.csv'
            csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            # Read Excel file and save it as CSV
            df = pd.read_excel(filepath)
            df.to_csv(csv_filepath, index=False)
            run_selected_lines_from_sql(sql_file_path='db_tools.sql', line_numbers=[0,1,2,3,4,5])
            # Import CSV into database
            import_csv_to_db(csv_filepath)
            return f"File uploaded, converted to CSV, and imported into the database: {csv_filename}"
    
    return '''
    <!doctype html>
    <title>Upload an Excel file</title>
    <h1>Upload an Excel file</h1>
    <form action="" method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''



if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
