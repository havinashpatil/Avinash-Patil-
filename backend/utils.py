"""
Utility functions for Blood Sense AI backend.
"""
import os
from werkzeug.utils import secure_filename
from PIL import Image
from typing import Tuple, Optional
from config import Config


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def validate_image(file) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file.
    Returns: (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"Invalid file type. Allowed: {', '.join(Config.ALLOWED_EXTENSIONS)}"
    
    # Check file size (if possible)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > Config.MAX_UPLOAD_SIZE:
        max_mb = Config.MAX_UPLOAD_SIZE / (1024 * 1024)
        return False, f"File too large. Maximum size: {max_mb}MB"
    
    # Try to open as image
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)  # Reset after verification
        return True, None
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def save_upload(file, subfolder: str = "") -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Save uploaded file to disk.
    Returns: (success, file_path, error_message)
    """
    try:
        # Validate file
        is_valid, error = validate_image(file)
        if not is_valid:
            return False, None, error
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Create unique filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base, ext = os.path.splitext(filename)
        unique_filename = f"{base}_{timestamp}{ext}"
        
        # Create upload directory
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, subfolder)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        return True, file_path, None
        
    except Exception as e:
        return False, None, f"Error saving file: {str(e)}"


def format_prediction_response(prediction_result: dict, scan_id: str = None) -> dict:
    """Format ML model prediction result for API response"""
    response = {
        'predicted_class': prediction_result.get('class', 'UNKNOWN'),
        'confidence': round(prediction_result.get('confidence', 0.0) * 100, 2),
        'all_probabilities': {
            k: round(v * 100, 2) 
            for k, v in prediction_result.get('all_probabilities', {}).items()
        },
        'recall_note': prediction_result.get('recall_note', ''),
        'model_loaded': prediction_result.get('model_loaded', False)
    }
    
    if scan_id:
        response['scan_id'] = scan_id
    
    # Determine priority based on class
    malignant_keywords = ['blast', 'malignant', 'cancer', 'leukemia']
    predicted_class_lower = response['predicted_class'].lower()
    
    is_high_priority = any(keyword in predicted_class_lower for keyword in malignant_keywords)
    response['priority'] = 'high' if is_high_priority else 'normal'
    
    return response


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def clean_old_uploads(days_old: int = 30):
    """
    Clean up old uploaded files (for maintenance).
    This should be run periodically as a background task.
    """
    import time
    from pathlib import Path
    
    upload_path = Path(Config.UPLOAD_FOLDER)
    current_time = time.time()
    cutoff_time = current_time - (days_old * 86400)  # days to seconds
    
    deleted_count = 0
    
    for file_path in upload_path.rglob('*'):
        if file_path.is_file():
            file_modified = file_path.stat().st_mtime
            if file_modified < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    
    return deleted_count
