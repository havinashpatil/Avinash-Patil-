# Blood Sense AI Backend

Backend API server for the Blood Sense AI blood cancer detection system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MongoDB:
```bash
# Install MongoDB if not already installed
# Start MongoDB service
mongod
```

3. Configure environment:
```bash
cp ../.env.example ../.env
# Edit .env with your configuration
```

4. Run the server:
```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

### Model
- `GET /api/model/health` - Model health check
- `GET /api/model/metrics` - Get performance metrics
- `GET /api/model/info` - Get model information

### Predictions
- `POST /api/predict/single` - Predict single image
- `POST /api/predict/batch` - Predict multiple images
- `GET /api/predictions/:id` - Get prediction details

### Scans
- `GET /api/scans` - List scans
- `GET /api/scans/:id` - Get scan details
- `PATCH /api/scans/:id` - Update scan
- `GET /api/scans/priority` - Get high-priority scans

### Reports
- `POST /api/reports` - Create report
- `GET /api/reports/:scanId` - Get report

### Statistics
- `GET /api/statistics` - Get system statistics

## Demo Users

After first run, demo users are created:
- **Technician**: `tech_demo` / `demo123`
- **Clinician**: `doc_demo` / `demo123`
