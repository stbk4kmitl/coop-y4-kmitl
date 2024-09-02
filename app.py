from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import psycopg2
from psycopg2 import sql


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}
DATABASE_URL = "postgresql://postgres:2002@localhost:5432/Database for Project "


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def check_temp_files(folder):
    return any(os.path.isfile(os.path.join(folder, f)) for f in  os.listdir(folder))

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

def delete_files_in_temp(temp_folder):
    try:
        files = os.listdir(temp_folder)
        for file in files:
            file_path = os.path.join(temp_folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Deleted all files in temp folder.")
    except OSError as e:
        print(f"Error while deleting files in temp folder: {e}")



###########################################################################

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

"""
def query_racks():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT MAX(rack_) FROM hardwarenames")
    max_rack = cur.fetchone()[0]
    for rack_value in range(1, max_rack + 1):
        cur.execute("""
#    """        SELECT * 
#            FROM hardwarenames
#            WHERE rack_ = %s
#            ORDER BY unit_ DESC
#        """, (rack_value,))
#    """2    results = cur.fetchall()
#        print(f"Results for rack_ = {rack_value}:")
#        for row in results:
#            print(row)
#        print("\n")

#    cur.close()
#    conn.close()
"""
def get_rack_values():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT rack_ FROM hardwarenames ORDER BY rack_")
    rack_values = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rack_values
"""

################################################################


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('home'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('home'))
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        
            # Convert Excel file to CSV
            csv_filename = filename.rsplit('.', 1)[0] + '.csv'
            csv_filepath = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            
            # อ่านไฟล์ Excel และบันทึกเป็น CSV
            df = pd.read_excel(filepath)
            df.to_csv(csv_filepath, index=False)
            
            # รันโค้ด SQL จากไฟล์ db_tools.sql
            run_selected_lines_from_sql(sql_file_path='db_tools.sql', line_numbers=[0,1,2,3,4])
            
            # นำเข้าข้อมูล CSV ไปยังฐานข้อมูล
            import_csv_to_db(csv_filepath)

            #query_racks()
            #run_selected_lines_from_sql(sql_file_path='db_tools.sql', line_numbers=[10,11,12,13,14,15,16,17,18,19,20,21,22,23,24])
            #rack_values = get_rack_values()
            #print("********************************", rack_values)
            # เปลี่ยนไปยังหน้า display.html
        return redirect(url_for('display'))
    if check_temp_files(app.config['UPLOAD_FOLDER']):
        return redirect(url_for('display'))
    return render_template('home.html')
    

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/display')
def display():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
            SELECT * 
            FROM hardwarenames
            ORDER BY unit_ DESC
        """)
    rows = cur.fetchall()
    cur.close()
    return render_template('display.html', rows=rows)
    

@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route('/save')
def save():
    return render_template('save.html')

@app.route('/export')
def export():
    return render_template('export.html')

@app.route('/delete_files', methods=['POST'])
def delete_files():
    delete_files_in_temp(app.config['UPLOAD_FOLDER'])
    run_selected_lines_from_sql(sql_file_path='db_tools.sql', line_numbers=[6])

    return redirect(url_for('home'))

# เริ่ม Flask Application
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)


