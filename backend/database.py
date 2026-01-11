"""
Database operations for Blood Sense AI.
Provides MongoDB connection and CRUD operations for all collections.
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from bson.objectid import ObjectId
from typing import Optional, List, Dict, Any
import os


class Database:
    """MongoDB database manager"""
    
    def __init__(self, uri: str, db_name: str):
        """Initialize database connection"""
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self._init_collections()
        self._create_indexes()
        print(f"✅ Connected to MongoDB database: {db_name}")
    
    def _init_collections(self):
        """Initialize collection references"""
        self.users = self.db.users
        self.patients = self.db.patients
        self.scans = self.db.scans
        self.predictions = self.db.predictions
        self.reports = self.db.reports
    
    def _create_indexes(self):
        """Create indexes for performance"""
        # User indexes
        self.users.create_index([("username", ASCENDING)], unique=True)
        self.users.create_index([("email", ASCENDING)], unique=True)
        
        # Scan indexes
        self.scans.create_index([("created_at", DESCENDING)])
        self.scans.create_index([("priority", ASCENDING)])
        self.scans.create_index([("status", ASCENDING)])
        self.scans.create_index([("patient_id", ASCENDING)])
        
        # Prediction indexes
        self.predictions.create_index([("scan_id", ASCENDING)])
        
        # Report indexes
        self.reports.create_index([("scan_id", ASCENDING)])
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username: str, password_hash: str, role: str, email: str) -> str:
        """Create a new user"""
        user_doc = {
            "username": username,
            "password_hash": password_hash,
            "role": role,  # 'technician' or 'clinician'
            "email": email,
            "created_at": datetime.utcnow()
        }
        result = self.users.insert_one(user_doc)
        return str(result.inserted_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        user = self.users.find_one({"username": username})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except:
            return None
    
    # ==================== PATIENT OPERATIONS ====================
    
    def create_patient(self, name: str, age: int, gender: str, patient_id: str) -> str:
        """Create a new patient record"""
        patient_doc = {
            "name": name,
            "age": age,
            "gender": gender,
            "patient_id": patient_id,
            "created_at": datetime.utcnow()
        }
        result = self.patients.insert_one(patient_doc)
        return str(result.inserted_id)
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Get patient by ID"""
        try:
            patient = self.patients.find_one({"_id": ObjectId(patient_id)})
            if patient:
                patient['_id'] = str(patient['_id'])
            return patient
        except:
            return None
    
    def get_patient_by_patient_id(self, patient_id: str) -> Optional[Dict]:
        """Get patient by patient_id field"""
        patient = self.patients.find_one({"patient_id": patient_id})
        if patient:
            patient['_id'] = str(patient['_id'])
        return patient
    
    # ==================== SCAN OPERATIONS ====================
    
    def create_scan(self, patient_id: str, image_path: str, uploaded_by: str) -> str:
        """Create a new scan record"""
        scan_doc = {
            "patient_id": patient_id,
            "image_path": image_path,
            "uploaded_by": uploaded_by,
            "status": "processing",  # processing, completed, reviewed
            "priority": "normal",    # normal, high
            "created_at": datetime.utcnow()
        }
        result = self.scans.insert_one(scan_doc)
        return str(result.inserted_id)
    
    def get_scan_by_id(self, scan_id: str) -> Optional[Dict]:
        """Get scan by ID"""
        try:
            scan = self.scans.find_one({"_id": ObjectId(scan_id)})
            if scan:
                scan['_id'] = str(scan['_id'])
            return scan
        except:
            return None
    
    def update_scan(self, scan_id: str, updates: Dict) -> bool:
        """Update scan record"""
        try:
            result = self.scans.update_one(
                {"_id": ObjectId(scan_id)},
                {"$set": updates}
            )
            return result.modified_count > 0
        except:
            return False
    
    def get_scans(self, filters: Dict = None, limit: int = 50, skip: int = 0) -> List[Dict]:
        """Get scans with optional filters"""
        if filters is None:
            filters = {}
        
        scans = list(self.scans.find(filters)
                     .sort("created_at", DESCENDING)
                     .skip(skip)
                     .limit(limit))
        
        for scan in scans:
            scan['_id'] = str(scan['_id'])
        
        return scans
    
    def get_priority_scans(self, limit: int = 50) -> List[Dict]:
        """Get high-priority scans (malignancy detected)"""
        return self.get_scans(
            filters={"priority": "high", "status": {"$ne": "reviewed"}},
            limit=limit
        )
    
    # ==================== PREDICTION OPERATIONS ====================
    
    def create_prediction(self, scan_id: str, predicted_class: str, 
                         confidence: float, all_probabilities: Dict,
                         recall_note: str = "") -> str:
        """Create a prediction record"""
        prediction_doc = {
            "scan_id": scan_id,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "all_probabilities": all_probabilities,
            "recall_note": recall_note,
            "created_at": datetime.utcnow()
        }
        result = self.predictions.insert_one(prediction_doc)
        return str(result.inserted_id)
    
    def get_prediction_by_scan_id(self, scan_id: str) -> Optional[Dict]:
        """Get prediction for a scan"""
        prediction = self.predictions.find_one({"scan_id": scan_id})
        if prediction:
            prediction['_id'] = str(prediction['_id'])
        return prediction
    
    def get_prediction_by_id(self, prediction_id: str) -> Optional[Dict]:
        """Get prediction by ID"""
        try:
            prediction = self.predictions.find_one({"_id": ObjectId(prediction_id)})
            if prediction:
                prediction['_id'] = str(prediction['_id'])
            return prediction
        except:
            return None
    
    # ==================== REPORT OPERATIONS ====================
    
    def create_report(self, scan_id: str, reviewed_by: str, notes: str = "") -> str:
        """Create a diagnostic report"""
        report_doc = {
            "scan_id": scan_id,
            "reviewed_by": reviewed_by,
            "notes": notes,
            "finalized_at": datetime.utcnow()
        }
        result = self.reports.insert_one(report_doc)
        
        # Update scan status to reviewed
        self.update_scan(scan_id, {"status": "reviewed"})
        
        return str(result.inserted_id)
    
    def get_report_by_scan_id(self, scan_id: str) -> Optional[Dict]:
        """Get report for a scan"""
        report = self.reports.find_one({"scan_id": scan_id})
        if report:
            report['_id'] = str(report['_id'])
        return report
    
    def get_report_by_id(self, report_id: str) -> Optional[Dict]:
        """Get report by ID"""
        try:
            report = self.reports.find_one({"_id": ObjectId(report_id)})
            if report:
                report['_id'] = str(report['_id'])
            return report
        except:
            return None
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self, user_role: str = None) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            "total_scans": self.scans.count_documents({}),
            "pending_review": self.scans.count_documents({"status": {"$ne": "reviewed"}}),
            "high_priority": self.scans.count_documents({"priority": "high"}),
            "reviewed": self.scans.count_documents({"status": "reviewed"}),
            "total_patients": self.patients.count_documents({})
        }
        
        # Get scans by status
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_counts = list(self.scans.aggregate(pipeline))
        stats["by_status"] = {item["_id"]: item["count"] for item in status_counts}
        
        return stats
    
    def seed_demo_data(self):
        """Seed database with demo users for testing"""
        import bcrypt
        
        # Check if users already exist
        if self.users.count_documents({}) > 0:
            print("⚠️  Database already has users, skipping seed")
            return
        
        # Create demo users
        demo_users = [
            {
                "username": "tech_demo",
                "password": "demo123",
                "role": "technician",
                "email": "technician@bloodsense.ai"
            },
            {
                "username": "doc_demo",
                "password": "demo123",
                "role": "clinician",
                "email": "clinician@bloodsense.ai"
            }
        ]
        
        for user in demo_users:
            password_hash = bcrypt.hashpw(
                user["password"].encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            
            self.create_user(
                username=user["username"],
                password_hash=password_hash,
                role=user["role"],
                email=user["email"]
            )
        
        print("✅ Demo users created:")
        print("   - Technician: tech_demo / demo123")
        print("   - Clinician: doc_demo / demo123")


# Singleton database instance
_db_instance = None


def get_db(uri: str = None, db_name: str = None) -> Database:
    """Get database instance (singleton pattern)"""
    global _db_instance
    
    if _db_instance is None:
        from config import get_config
        config = get_config()
        
        uri = uri or config.MONGODB_URI
        db_name = db_name or config.MONGODB_DB_NAME
        
        _db_instance = Database(uri, db_name)
    
    return _db_instance
