from flask import Flask, send_file, abort, send_from_directory
import os
import zipfile

app = Flask(__name__, static_url_path='/static')
DATA_ROOT = "/media/coursework/Segate4.12_SOLAR/SOLAR_DATA_GBD"

@app.route('/')
def home():
    return send_file("twin_webpage.htm")

@app.route('/check-data/<date>')
def check_data(date):
    year, month, day = date.split('_')
    
    csv_path = os.path.join(DATA_ROOT, "combined", year, month, f"{date}.csv")
    folder_path = os.path.join(DATA_ROOT, "raw", year, month, f"{date}")

    print("Checking:", csv_path)
    print("Folder:", folder_path)

    if os.path.exists(csv_path) or os.path.isdir(folder_path):
        return '', 200
    else:
        return abort(404)

@app.route('/download/README')
def download_readme():
    return send_from_directory('downloads', 'README.pdf', as_attachment=True)

@app.route('/download/twin_data_process_raw')
def download_script1():
    return send_from_directory('downloads', 'twin_data_process_raw.py', as_attachment=True)

@app.route('/download/twin_data_process_combined')
def download_script2():
    return send_from_directory('downloads', 'twin_data_process_combined.py', as_attachment=True)

@app.route('/SOLAR_DATA_GBD/combined/<year>/<month>/<date>')
def get_csv(year, month, date):
    csv_path = os.path.join(DATA_ROOT, "combined", year, month)
    return send_from_directory(csv_path, f"{date}.csv", as_attachment=True)

@app.route('/SOLAR_DATA_GBD/raw/<year>/<month>/<date>')
def download_folder(year, month, date):
    folder_path = os.path.join(DATA_ROOT, "raw", year, month, date)
    if not os.path.isdir(folder_path):
        return abort(404)

    zip_path = f'{folder_path}.zip'

    # Zip it
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)
    
    # Send the zip
    try:
        return send_file(zip_path, as_attachment=True)
    finally:
        os.remove(zip_path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)

