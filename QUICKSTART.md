# Blood Sense AI - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Prerequisites
- Python 3.9+ installed
- Node.js 16+ installed
- MongoDB installed and running

### Step 1: Install Backend Dependencies
```bash
cd BloodCancerCellDetectAIModel
pip install -r backend/requirements.txt
```

### Step 2: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 3: Setup Environment
```bash
# Copy and edit environment file
copy .env.example .env
```

Note: For initial testing, the default `.env.example` values work fine.

### Step 4: Start MongoDB
```bash
# Windows (run as service or manually):
mongod

# Linux/macOS:
sudo systemctl start mongodb
```

### Step 5: Start Backend Server
```bash
cd backend
python app.py
```

Keep this terminal running. You should see:
```
✅ Connected to MongoDB database: bloodsense
✅ Model loaded successfully
✅ Demo users created
```

### Step 6: Start Frontend (New Terminal)
```bash
cd frontend
npm start
```

Browser will open automatically to `http://localhost:3000`

## 🎯 Testing the System

### Login
- Click **"Technician"** demo button (auto-login as `tech_demo`)
- Or click **"Clinician"** demo button (auto-login as `doc_demo`)

### As Technician:
1. Upload a blood smear image
2. View AI prediction result
3. Check if malignant cells trigger alert

### As Clinician:
1. View priority queue
2. Select a high-priority scan
3. Review cell distribution chart
4. Add clinical notes
5. Finalize report

## ⚠️ Important Notes

1. **Model File**: If `blood_cell_model.keras` doesn't exist, you'll need to train the model first
2. **Demo Users**: System creates these automatically:
   - Technician: `tech_demo` / `demo123`
   - Clinician: `doc_demo` / `demo123`
3. **Ports**: Backend runs on 5000, Frontend on 3000

## 🐛 Troubleshooting

**"Model not loaded"**: Run training script first (`python train.py`)
**"MongoDB connection error"**: Ensure MongoDB is running
**"Port already in use"**: Kill process on that port and restart

---

For detailed documentation, see [README.md](README.md)
