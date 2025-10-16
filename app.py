from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS 
import os
import uuid 

# Inicialización de la aplicación Flask
app = Flask(__name__)

# 🚩 Configuración de CORS: Esencial para que el frontend (3000) pueda hablar con el backend (5000)
# Permitimos peticiones POST al endpoint /api/* desde http://localhost:3000
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Directorio donde se guardarán los archivos subidos.
UPLOAD_FOLDER = 'uploads' 
# Crea la carpeta 'uploads' si no existe dentro de 'backend'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- ENDPOINT DE SUBIDA DE IMAGEN (POST) ---
@app.route('/api/upload-design', methods=['POST'])
def upload_design():
    """Recibe el archivo de imagen del frontend, lo guarda y devuelve su URL pública."""
    
    # 1. Verificar si el campo 'designImage' (el nombre usado en Next.js) fue enviado.
    if 'designImage' not in request.files:
        return jsonify({"error": "No se encontró el archivo 'designImage' en la petición."}), 400

    file = request.files['designImage']
    
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    # 2. Generar un nombre de archivo único con UUID para evitar conflictos (ej: d949c58e-0f8b-4b71-b51f-29d068597f48.jpg)
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    unique_filename = str(uuid.uuid4()) + '.' + ext
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    # 3. Guardar el archivo en el disco dentro de la carpeta 'uploads'
    try:
        file.save(file_path)
    except Exception as e:
        # Esto captura errores de escritura de disco
        return jsonify({"error": f"Error al guardar el archivo: {e}"}), 500

    # 4. Devolver la URL COMPLETA. Esta es la URL que Next.js debe guardar en localStorage.
    # Esta URL usa el endpoint que se define en el siguiente @app.route
    public_url = f"http://localhost:5000/uploads/{unique_filename}" 
    
    return jsonify({
        "message": "Archivo subido con éxito",
        "imageUrl": public_url
    }), 200

# --- ENDPOINT PARA SERVIR LOS ARCHIVOS (GET) ---
@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Permite que el navegador acceda a http://localhost:5000/uploads/nombre.jpg."""
    # Retorna el archivo solicitado desde la carpeta 'uploads'
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # 🚩 Inicia Flask en el puerto 5000, separado de Next.js (3000)
    app.run(debug=True, port=5000)
