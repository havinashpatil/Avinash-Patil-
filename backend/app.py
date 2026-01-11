"""
Blood Sense AI - Main Flask Application
Provides REST API for the blood cancer detection system.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from werkzeug.exceptions import RequestEntityTooLarge
import os
import sys

# Add parent directory to path to import model module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config
from database import get_db
from auth import (
    authenticate_user, create_token, require_role,
    get_current_user, register_user, success_response, error_response
)
from utils import save_upload, format_prediction_response
from model import get_model_manager


# Initialize Flask app
app = Flask(__name__)
config = get_config()

# Configuration
app.config.from_object(config)
config.init_app()

# Initialize extensions
CORS(app, origins=[config.FRONTEND_URL])
jwt = JWTManager(app)

# Initialize database
db = get_db()

# Initialize model manager
model_manager = get_model_manager()


# ==================== ERROR HANDLERS ====================

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return error_response("File too large", str(e), 413)


@app.errorhandler(404)
def handle_not_found(e):
    return error_response("Resource not found", str(e), 404)


@app.errorhandler(500)
def handle_server_error(e):
    return error_response("Internal server error", str(e), 500)


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return error_response("Missing username or password")
    
    username = data['username']
    password = data['password']
    
    # Authenticate user
    success, user_data, error = authenticate_user(username, password)
    
    if not success:
        return error_response(error, status_code=401)
    
    # Create JWT token
    token = create_token(user_data)
    
    return success_response({
        'token': token,
        'user': user_data
    }, "Login successful")


@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint (admin only in production)"""
    data = request.get_json()
    
    required_fields = ['username', 'password', 'role', 'email']
    if not all(field in data for field in required_fields):
        return error_response("Missing required fields")
    
    success, user_id, error = register_user(
        data['username'],
        data['password'],
        data['role'],
        data['email']
    )
    
    if not success:
        return error_response(error)
    
    return success_response({
        'user_id': user_id
    }, "User registered successfully", 201)


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user info"""
    user = get_current_user()
    
    if not user:
        return error_response("User not found", status_code=401)
    
    # Get full user data from database
    user_data = db.get_user_by_id(user['id'])
    
    if not user_data:
        return error_response("User not found", status_code=404)
    
    # Remove sensitive data
    user_data.pop('password_hash', None)
    
    return success_response({'user': user_data})


# ==================== MODEL ENDPOINTS ====================

@app.route('/api/model/health', methods=['GET'])
def model_health():
    """Check if model is loaded and ready"""
    info = model_manager.get_model_info()
    
    if not info['model_loaded']:
        return error_response("Model not loaded", status_code=503)
    
    return success_response({
        'status': 'healthy',
        'model_loaded': True,
        'classes': info['classes'],
        'num_classes': info['num_classes']
    }, "Model is ready")


@app.route('/api/model/metrics', methods=['GET'])
def model_metrics():
    """Get model performance metrics"""
    metrics = model_manager.get_model_metrics()
    
    return success_response({
        'metrics': metrics
    }, "Metrics retrieved successfully")


@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    info = model_manager.get_model_info()
    metrics = model_manager.get_model_metrics()
    
    return success_response({
        'model_info': info,
        'last_trained': metrics.get('last_trained', 'unknown'),
        'accuracy': metrics.get('accuracy', 0.0)
    }, "Model info retrieved successfully")


# ==================== PREDICTION ENDPOINTS ====================

@app.route('/api/predict/single', methods=['POST'])
@require_role('technician', 'clinician')
def predict_single():
    """Upload and predict single image"""
    user = get_current_user()
    
    # Check if file is present
    if 'file' not in request.files:
        return error_response("No file provided")
    
    file = request.files['file']
    
    # Get optional patient info
    patient_id = request.form.get('patient_id', 'UNKNOWN')
    patient_name = request.form.get('patient_name', 'Unknown Patient')
    
    # Save uploaded file
    success, file_path, error = save_upload(file, subfolder='scans')
    
    if not success:
        return error_response(error)
    
    # Create scan record
    scan_id = db.create_scan(
        patient_id=patient_id,
        image_path=file_path,
        uploaded_by=user['id']
    )
    
    # Run prediction
    prediction_result = model_manager.predict_single_image(file_path)
    
    if 'error' in prediction_result:
        db.update_scan(scan_id, {'status': 'failed'})
        return error_response(prediction_result['error'])
    
    # Format response
    response_data = format_prediction_response(prediction_result, scan_id)
    
    # Save prediction to database
    db.create_prediction(
        scan_id=scan_id,
        predicted_class=prediction_result['class'],
        confidence=prediction_result['confidence'],
        all_probabilities=prediction_result['all_probabilities'],
        recall_note=prediction_result['recall_note']
    )
    
    # Update scan with prediction results
    db.update_scan(scan_id, {
        'status': 'completed',
        'priority': response_data['priority']
    })
    
    return success_response(response_data, "Prediction completed successfully", 201)


@app.route('/api/predict/batch', methods=['POST'])
@require_role('technician', 'clinician')
def predict_batch():
    """Upload and predict multiple images"""
    user = get_current_user()
    
    # Check if files are present
    if 'files' not in request.files:
        return error_response("No files provided")
    
    files = request.files.getlist('files')
    
    if not files or len(files) == 0:
        return error_response("No files selected")
    
    # Get optional patient info
    patient_id = request.form.get('patient_id', 'UNKNOWN')
    
    results = []
    scan_ids = []
    
    for file in files:
        # Save file
        success, file_path, error = save_upload(file, subfolder='scans')
        
        if not success:
            results.append({
                'filename': file.filename,
                'error': error,
                'success': False
            })
            continue
        
        # Create scan record
        scan_id = db.create_scan(
            patient_id=patient_id,
            image_path=file_path,
            uploaded_by=user['id']
        )
        scan_ids.append(scan_id)
        
        # Run prediction
        prediction_result = model_manager.predict_single_image(file_path)
        
        if 'error' in prediction_result:
            db.update_scan(scan_id, {'status': 'failed'})
            results.append({
                'filename': file.filename,
                'scan_id': scan_id,
                'error': prediction_result['error'],
                'success': False
            })
            continue
        
        # Format response
        response_data = format_prediction_response(prediction_result, scan_id)
        response_data['filename'] = file.filename
        response_data['success'] = True
        
        # Save prediction
        db.create_prediction(
            scan_id=scan_id,
            predicted_class=prediction_result['class'],
            confidence=prediction_result['confidence'],
            all_probabilities=prediction_result['all_probabilities'],
            recall_note=prediction_result['recall_note']
        )
        
        # Update scan
        db.update_scan(scan_id, {
            'status': 'completed',
            'priority': response_data['priority']
        })
        
        results.append(response_data)
    
    # Calculate summary statistics
    successful_predictions = [r for r in results if r.get('success', False)]
    high_priority_count = len([r for r in successful_predictions if r.get('priority') == 'high'])
    
    return success_response({
        'results': results,
        'summary': {
            'total_images': len(files),
            'successful': len(successful_predictions),
            'failed': len(files) - len(successful_predictions),
            'high_priority': high_priority_count
        }
    }, "Batch prediction completed", 201)


@app.route('/api/predictions/<prediction_id>', methods=['GET'])
@jwt_required()
def get_prediction(prediction_id):
    """Get prediction details"""
    prediction = db.get_prediction_by_id(prediction_id)
    
    if not prediction:
        return error_response("Prediction not found", status_code=404)
    
    return success_response({'prediction': prediction})


# ==================== SCAN MANAGEMENT ENDPOINTS ====================

@app.route('/api/scans', methods=['GET'])
@jwt_required()
def get_scans():
    """Get scans (filtered by role and query parameters)"""
    user = get_current_user()
    
    # Get query parameters
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    # Build filters
    filters = {}
    if status:
        filters['status'] = status
    if priority:
        filters['priority'] = priority
    
    # Role-based filtering
    if user['role'] == 'technician':
        # Technicians see scans they uploaded
        filters['uploaded_by'] = user['id']
    
    # Get scans
    scans = db.get_scans(filters=filters, limit=limit, skip=skip)
    
    # Enrich with predictions
    for scan in scans:
        prediction = db.get_prediction_by_scan_id(scan['_id'])
        if prediction:
            scan['prediction'] = prediction
    
    return success_response({
        'scans': scans,
        'count': len(scans)
    })


@app.route('/api/scans/<scan_id>', methods=['GET'])
@jwt_required()
def get_scan(scan_id):
    """Get scan details"""
    scan = db.get_scan_by_id(scan_id)
    
    if not scan:
        return error_response("Scan not found", status_code=404)
    
    # Get associated prediction
    prediction = db.get_prediction_by_scan_id(scan_id)
    if prediction:
        scan['prediction'] = prediction
    
    # Get associated report
    report = db.get_report_by_scan_id(scan_id)
    if report:
        scan['report'] = report
    
    return success_response({'scan': scan})


@app.route('/api/scans/<scan_id>', methods=['PATCH'])
@require_role('clinician')
def update_scan(scan_id):
    """Update scan (clinician only)"""
    data = request.get_json()
    
    scan = db.get_scan_by_id(scan_id)
    if not scan:
        return error_response("Scan not found", status_code=404)
    
    # Update scan
    success = db.update_scan(scan_id, data)
    
    if not success:
        return error_response("Failed to update scan")
    
    return success_response({'scan_id': scan_id}, "Scan updated successfully")


@app.route('/api/scans/priority', methods=['GET'])
@require_role('clinician')
def get_priority_scans():
    """Get high-priority scans (clinician only)"""
    limit = int(request.args.get('limit', 50))
    
    scans = db.get_priority_scans(limit=limit)
    
    # Enrich with predictions
    for scan in scans:
        prediction = db.get_prediction_by_scan_id(scan['_id'])
        if prediction:
            scan['prediction'] = prediction
    
    return success_response({
        'scans': scans,
        'count': len(scans)
    })


# ==================== REPORT ENDPOINTS ====================

@app.route('/api/reports', methods=['POST'])
@require_role('clinician')
def create_report():
    """Create diagnostic report (clinician only)"""
    user = get_current_user()
    data = request.get_json()
    
    if not data or 'scan_id' not in data:
        return error_response("Missing scan_id")
    
    scan_id = data['scan_id']
    notes = data.get('notes', '')
    
    # Verify scan exists
    scan = db.get_scan_by_id(scan_id)
    if not scan:
        return error_response("Scan not found", status_code=404)
    
    # Create report
    report_id = db.create_report(
        scan_id=scan_id,
        reviewed_by=user['id'],
        notes=notes
    )
    
    return success_response({
        'report_id': report_id,
        'scan_id': scan_id
    }, "Report created successfully", 201)


@app.route('/api/reports/<scan_id>', methods=['GET'])
@jwt_required()
def get_report(scan_id):
    """Get report for a scan"""
    report = db.get_report_by_scan_id(scan_id)
    
    if not report:
        return error_response("Report not found", status_code=404)
    
    # Get scan and prediction for complete report
    scan = db.get_scan_by_id(scan_id)
    prediction = db.get_prediction_by_scan_id(scan_id)
    
    report['scan'] = scan
    report['prediction'] = prediction
    
    return success_response({'report': report})


# ==================== STATISTICS ENDPOINTS ====================

@app.route('/api/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get system statistics"""
    user = get_current_user()
    
    stats = db.get_statistics(user_role=user['role'])
    
    return success_response({'statistics': stats})


# ==================== FILE SERVING ====================

@app.route('/api/uploads/<path:filename>', methods=['GET'])
@jwt_required()
def serve_upload(filename):
    """Serve uploaded files (authenticated users only)"""
    return send_from_directory(config.UPLOAD_FOLDER, filename)


# ==================== ROOT ENDPOINT ====================

@app.route('/', methods=['GET'])
def index():
    """API root endpoint"""
    return jsonify({
        'name': 'Blood Sense AI API',
        'version': '1.0.0',
        'status': 'running',
        'model_loaded': model_manager.model_loaded
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'model': 'loaded' if model_manager.model_loaded else 'not loaded'
    })


# ==================== INITIALIZATION ====================

def init_app():
    """Initialize application (seed database, etc.)"""
    print("\n🚀 Initializing Blood Sense AI Application...")
    
    # Seed demo users if needed
    db.seed_demo_data()
    
    print("\n✅ Application initialized successfully!")
    print(f"   - Database: Connected")
    print(f"   - Model: {'Loaded' if model_manager.model_loaded else 'Not Loaded'}")
    print(f"   - Upload folder: {config.UPLOAD_FOLDER}")
    print(f"\n🌐 Starting server on {config.HOST}:{config.PORT}...")


if __name__ == '__main__':
    init_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
