from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import fitz
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output_images'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# 确保上传和输出文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def pdf_to_images(pdf_path, output_folder):
    converted_files = []
    with fitz.open(pdf_path) as doc:
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            output_image = f"{pdf_name}_{page_num}.png"
            pix.save(os.path.join(output_folder, output_image))
            converted_files.append(output_image)
    return converted_files


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(pdf_path)
            converted_files = pdf_to_images(pdf_path, app.config['OUTPUT_FOLDER'])
            return render_template('download.html', converted_files=converted_files)
    return render_template('upload.html')


@app.route('/output_images/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
