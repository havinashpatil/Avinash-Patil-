# Blood Sense AI - Complete System

A comprehensive AI-powered Blood Cancer Detection System with role-based access control, automated triage, and detailed diagnostic reporting.

## 🎯 Project Overview

Blood Sense AI replaces manual microscopic blood smear analysis with AI-powered objective diagnosis. The system is optimized for high sensitivity (recall) to ensure malignant blast cells are never missed.

### Key Features

- **🔬 AI-Powered Detection**: MobileNetV2-based deep learning model
- **⚡ Real-Time Triage**: Instant malignancy alerts for urgent review
- **👥 Role-Based Access**: Separate interfaces for technicians and clinicians
- **📊 Comprehensive Metrics**: Model recall and sensitivity tracking
- **🎨 Premium UI**: Modern glassmorphism design with Tailwind CSS
- **🔐 Secure Authentication**: JWT-based authentication with RBAC

## 🏗️ Architecture

```
BloodCancerCellDetectAIModel/
├── backend/                 # Flask REST API
│   ├── app.py              # Main application
│   ├── auth.py             # Authentication & RBAC
│   ├── database.py         # MongoDB operations
│   ├── config.py           # Configuration
│   ├── utils.py            # Utilities
│   └── requirements.txt    # Python dependencies
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Dashboard pages
│   │   ├── services/      # API services
│   │   └── context/       # React context
│   ├── public/
│   └── package.json
├── model.py               # ML model (inference)
├── train.py               # Model training script
├── .env.example           # Environment template
└── README.md             # This file
```

## 💻 System Requirements

### Hardware
- **CPU**: Intel i7 (8th Gen+) or AMD Ryzen 7
- **RAM**: 16GB DDR4 minimum
- **GPU**: NVIDIA RTX 3050 or higher (4GB+ VRAM) for inference
- **Storage**: 500GB NVMe SSD

### Software
- **Python**: 3.9 or higher
- **Node.js**: 16.x or higher
- **MongoDB**: 4.4 or higher
- **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS

## 🚀 Installation & Setup

### 1. Prerequisites

**Install MongoDB:**
```bash
# Windows: Download from https://www.mongodb.com/try/download/community
# Linux:
sudo apt-get install -y mongodb
sudo systemctl start mongodb

# macOS:
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Install Python and Node.js:**
- Python 3.9+: https://www.python.org/downloads/
- Node.js 16+: https://nodejs.org/

### 2. Backend Setup

```bash
# Navigate to project directory
cd BloodCancerCellDetectAIModel

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
# Important: Change JWT_SECRET_KEY in production!
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Return to project root
cd ..
```

### 5. Model Setup

**If you already have a trained model:**
- Ensure `blood_cell_model.keras` is in the project root
- Ensure `class_names.json` exists (will be created automatically if missing)

**To train a new model:**
```bash
python train.py
```

## 🎬 Running the Application

### Start Backend Server

```bash
# From project root, with virtual environment activated
cd backend
python app.py
```

The backend will start on `http://localhost:5000`

### Start Frontend Development Server

```bash
# In a new terminal, from project root
cd frontend
npm start
```

The frontend will start on `http://localhost:3000`

## 👤 Demo Users

After first run, demo users are automatically created:

| Role | Username | Password |
|------|----------|----------|
| **Technician** | `tech_demo` | `demo123` |
| **Clinician** | `doc_demo` | `demo123` |

## 📱 User Workflows

### Technician Workflow

1. **Login** with technician credentials
2. **Upload** blood smear images (single or batch)
3. **View** real-time AI prediction results
4. **Receive Alerts** for malignant cell detections
5. **Track** recent scan history

### Clinician Workflow

1. **Login** with clinician credentials
2. **Review Priority Queue** (high-priority scans first)
3. **Analyze** detailed prediction results and cell distribution
4. **Review** model recall metrics
5. **Add Clinical Notes** and finalize diagnostic reports
6. **Archive** reports to EMR database

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Model
- `GET /api/model/health` - Model health check
- `GET /api/model/metrics` - Performance metrics
- `GET /api/model/info` - Model information

### Predictions
- `POST /api/predict/single` - Single image prediction
- `POST /api/predict/batch` - Batch prediction

### Scans
- `GET /api/scans` - List scans
- `GET /api/scans/:id` - Get scan details
- `GET /api/scans/priority` - High-priority scans
- `PATCH /api/scans/:id` - Update scan

### Reports
- `POST /api/reports` - Create report
- `GET /api/reports/:scanId` - Get report

For detailed API documentation, see [backend/README.md](backend/README.md)

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Manual Testing
1. **Model Prediction**: Upload sample blood smear images
2. **Role Access**: Verify technician can't access clinician routes
3. **Triage Workflow**: Upload malignant cells → verify alert → clinician review
4. **Recall Metrics**: Check recall display on both dashboards

## 📊 Model Performance

The MobileNetV2 model is optimized for:
- **High Recall** (Sensitivity): Minimizes false negatives
- **Blast Cell Detection**: Prioritized for urgent review
- **Real-Time Inference**: Fast predictions for clinical workflow

Metrics are tracked in `model_metrics.json` after training.

## 🛡️ Security

- **JWT Authentication**: Secure token-based auth
- **Role-Based Access Control**: Separate permissions for technicians and clinicians
- **Input Validation**: File type and size validation
- **CORS Configuration**: Restricted to frontend URL
- **Password Hashing**: Bcrypt password protection

**Production Checklist:**
- [ ] Change `JWT_SECRET_KEY` in `.env`
- [ ] Enable HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Implement rate limiting

## 🎨 Design System

The frontend uses a premium medical theme with:
- **Glassmorphism**: Frosted glass effect cards
- **Color Palette**: Medical blues, greens, and urgent reds
- **Typography**: Inter and Outfit fonts
- **Animations**: Smooth transitions and micro-interactions
- **Responsive**: Mobile-first design

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Check MongoDB is running
mongod --version
sudo systemctl status mongodb

# Restart MongoDB
sudo systemctl restart mongodb
```

### Model Not Loading
- Verify `blood_cell_model.keras` exists in project root
- Check `class_names.json` exists
- Run `python model.py` to test model loading

### Frontend API Connection Error
- Verify backend is running on port 5000
- Check `.env` file has correct `FRONTEND_URL`
- Verify CORS is properly configured

### Port Already in Use
```bash
# Find and kill process using port
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/macOS:
lsof -ti:5000 | xargs kill
```

## 📝 License

This project is licensed for educational and research purposes.

## 👨‍💻 Development

Built with:
- **Backend**: Flask, MongoDB, TensorFlow
- **Frontend**: React, Tailwind CSS, Chart.js
- **ML**: MobileNetV2, Keras, scikit-learn

## 📧 Support

For issues and questions:
1. Check this README
2. Review [backend/README.md](backend/README.md)
3. Check the implementation plan and task documents

---

**Blood Sense AI** - Empowering Precision Hematology with AI 🔬
