from flask import Flask, render_template, request, send_file, jsonify
import os
import logging
from PyPDF2 import PdfMerger
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create folders if not exist
UPLOAD_FOLDER = "uploads"
MERGED_FOLDER = "merged"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return jsonify({"message": "Test route working", "method": "GET"})
    else:
        return jsonify({"message": "Test route working", "method": "POST", "data": dict(request.form)})

@app.route("/merge", methods=["POST", "OPTIONS"])
def merge():
    if request.method == "OPTIONS":
        # Handle preflight request
        response = jsonify({"message": "Options OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
    
    try:
        logger.info("Received merge request")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request content type: {request.content_type}")
        
        files = request.files.getlist("pdfs")
        custom_name = request.form.get("filename")

        logger.info(f"Number of files received: {len(files)}")
        logger.info(f"Custom filename: {custom_name}")

        if not files or len(files) == 0:
            logger.error("No files provided")
            return jsonify({"error": "No PDF files provided"}), 400

        if not custom_name:
            logger.error("No filename provided")
            return jsonify({"error": "Output filename is required"}), 400

        # Validate that we have actual files (not empty)
        valid_files = [f for f in files if f.filename and f.filename != '']
        if not valid_files:
            logger.error("No valid files provided")
            return jsonify({"error": "No valid PDF files provided"}), 400

        # Make sure the file ends with .pdf
        if not custom_name.lower().endswith(".pdf"):
            custom_name += ".pdf"

        # Secure filename and prepare path
        output_filename = secure_filename(custom_name)
        output_path = os.path.join(MERGED_FOLDER, output_filename)

        merger = PdfMerger()
        temp_files = []

        for i, file in enumerate(valid_files):
            logger.info(f"Processing file {i+1}: {file.filename}")
            
            if not file.filename.lower().endswith('.pdf'):
                logger.warning(f"Skipping non-PDF file: {file.filename}")
                continue
                
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, f"{i}_{filename}")
            file.save(temp_path)
            temp_files.append(temp_path)
            
            try:
                merger.append(temp_path)
                logger.info(f"Successfully added {filename} to merger")
            except Exception as e:
                logger.error(f"Error adding {filename} to merger: {e}")
                # Clean up files before returning error
                for temp in temp_files:
                    if os.path.exists(temp):
                        os.remove(temp)
                return jsonify({"error": f"Invalid PDF file: {filename}"}), 400

        if not temp_files:
            logger.error("No valid PDF files to merge")
            return jsonify({"error": "No valid PDF files found"}), 400

        logger.info(f"Writing merged PDF to: {output_path}")
        merger.write(output_path)
        merger.close()

        # Clean up temporary uploaded PDFs
        for temp in temp_files:
            if os.path.exists(temp):
                os.remove(temp)
                logger.info(f"Cleaned up temporary file: {temp}")

        logger.info("PDF merge completed successfully")
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        logger.error(f"Unexpected error during merge: {e}")
        # Clean up any temporary files
        if 'temp_files' in locals():
            for temp in temp_files:
                if os.path.exists(temp):
                    os.remove(temp)
        return jsonify({"error": f"Error while merging PDFs: {str(e)}"}), 500

if __name__ == "__main__":
    print("Starting Flask app on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
