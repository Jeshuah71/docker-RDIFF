from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/app/source'

BACKUP_DIR = '/app/backup'
RESTORE_DIR = '/app/restore'

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(RESTORE_DIR, exist_ok=True)

# Listar archivos en backup
def list_backed_up_files():
    files = []
    for root, dirs, filenames in os.walk(BACKUP_DIR):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), BACKUP_DIR)
            files.append(rel_path)
    return files

# Listar archivos restaurados
def list_restored_files():
    files = []
    for root, dirs, filenames in os.walk(RESTORE_DIR):
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), RESTORE_DIR)
            files.append(rel_path)
    return files

# Página principal
@app.route('/')
def index():
    return render_template("index.html", 
        backup_files=list_backed_up_files(),
        restored_files=list_restored_files())

# Subir archivo y hacer backup automático
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        subprocess.run(['rdiff-backup', app.config['UPLOAD_FOLDER'], BACKUP_DIR], check=True)
        return redirect(url_for('index'))

# Restaurar usando snapshot, creando subcarpeta por fecha
@app.route('/restore', methods=['POST'])
def restore_file():
    snapshot_date = request.form['snapshot_date'] or 'now'
    folder_suffix = snapshot_date.replace(':','_').replace('/','_').replace(' ','_')
    restore_path = os.path.join(RESTORE_DIR, f"restore_{folder_suffix}")
    os.makedirs(restore_path, exist_ok=True)

    try:
        subprocess.run([
            'rdiff-backup',
            '--force',
            '-r', snapshot_date,
            BACKUP_DIR,
            restore_path
        ], check=True)
        return jsonify({'success': True})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

# Vista previa de archivo restaurado
@app.route('/preview', methods=['POST'])
def preview_file():
    file_path = request.form['file_path']
    full_path = os.path.join(RESTORE_DIR, file_path)
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return jsonify({'content': content})
        except Exception as e:
            return jsonify({'error': str(e)})
    return jsonify({'error': 'File not found'}), 404

# Descargar archivo restaurado
@app.route('/download', methods=['POST'])
def download_file():
    file_path = request.form['file_path']
    full_path = os.path.join(RESTORE_DIR, file_path)
    if os.path.exists(full_path):
        return send_file(full_path, as_attachment=True)
    return "File not found", 404

# Ejecutar servidor
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    