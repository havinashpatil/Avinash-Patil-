# Blood Sense AI - Setup Fix Guide

## Issues Fixed:

### 1. ✅ Backend Import Errors
**Problem**: `ModuleNotFoundError: No module named 'backend'`
**Solution**: Changed all imports from `from backend.X` to `from X` (relative imports)

### 2. ✅ Pillow Python 3.13 Incompatibility  
**Problem**: Pillow 10.2.0 doesn't work with Python 3.13
**Solution**: Updated to Pillow 10.3.0 in requirements.txt

### 3. ✅ Frontend Dependencies Missing
**Problem**: `react-scripts not found`
**Solution**: Running `npm install` in frontend directory

---

## Step-by-Step Setup (Corrected):

### Step 1: Install Backend Dependencies

```bash
cd c:\Users\ADMIN\OneDrive\Desktop\BloodCancerCellDetectAIModel\backend
pip install -r requirements.txt
```

This should now work with the updated Pillow version.

### Step 2: Install Frontend Dependencies

```bash
cd ..\frontend
npm install
```

This is currently running and may take a few minutes.

### Step 3: Start MongoDB

Make sure MongoDB is running:
```bash
# Check if MongoDB is running
mongod --version

# If not running, start it
# Windows: Start MongoDB service from Services or run mongod.exe
```

### Step 4: Start Backend Server

```bash
cd ..\backend
python app.py
```

You should see:
```
✅ Connected to MongoDB database: bloodsense
✅ Model loaded successfully (or warning if model not trained yet)
✅ Demo users created
🌐 Starting server on 0.0.0.0:5000...
```

### Step 5: Start Frontend (New Terminal)

```bash
cd ..\frontend
npm start
```

Browser will open at `http://localhost:3000`

---

## Important Notes:

### If Model Not Found:
The system will work without the trained model, but predictions won't work. The model file `blood_cell_model.keras` needs to be in the project root. If you need to train it, that's a separate step.

### Demo Login:
- **Technician**: username `tech_demo`, password `demo123`
- **Clinician**: username `doc_demo`, password `demo123`

---

## Next Steps After Setup:

1. **Test Login**: Try logging in as technician or clinician
2. **Test Upload** (if you have sample images): Upload a blood smear image
3. **Explore UI**: Navigate through both dashboards

Let me know once the frontend install completes!
