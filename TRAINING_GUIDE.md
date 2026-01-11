# Blood Sense AI - Training Guide

## Why You Need to Train

You currently have:
- ✅ Training DATA (images at `C:\Users\ADMIN\OneDrive\Desktop\train`)  
- ❌ Trained MODEL file (`blood_cell_model.keras`) ← **This is missing!**

The system needs BOTH to work.

---

## How to Train the Model

### Quick Start:
```bash
cd c:\Users\ADMIN\OneDrive\Desktop\BloodCancerCellDetectAIModel
python train.py
```

### What Will Happen:
1. **Loads your training images** from `C:\Users\ADMIN\OneDrive\Desktop\train`
2. **Splits data** into 80% training / 20% validation
3. **Trains MobileNetV2** model for 10 epochs (~5-15 minutes)
4. **Calculates metrics** (accuracy, recall, precision)
5. **Saves 3 files**:
   - `blood_cell_model.keras` ← The trained AI brain
   - `class_names.json` ← List of cell types
   - `model_metrics.json` ← Performance metrics

### Training Parameters (in train.py):
```python
EPOCHS = 10          # Number of training cycles
BATCH_SIZE = 32      # Images per batch
LEARNING_RATE = 0.001 # How fast the model learns
```

You can edit these if needed for better results.

---

## After Training

Once `python train.py` completes successfully:

1. ✅ **Test the model**:
   ```bash
   python model.py
   ```
   Should show: "✅ Model is ready for predictions"

2. ✅ **Restart backend** (if already running):
   - Stop the current backend (Ctrl+C)
   - Start again: `python backend/app.py`
   - It will now load the trained model

3. ✅ **Upload images via web interface**:
   - Go to `http://localhost:3000`
   - Login as technician
   - Upload blood cell images
   - See REAL AI predictions!

---

## Expected Training Output:

```
🔬 Blood Sense AI - Model Training
================================
📂 Loading training data...
✅ Found 4 classes: ['Blast', 'Lymphocyte', 'Monocyte', 'Neutrophil']
✅ Training batches: 64
✅ Validation batches: 16

🔨 Building model for 4 classes...
✅ Model built successfully

🚀 Starting training for 10 epochs...
Epoch 1/10
64/64 [==============================] - 45s 701ms/step - accuracy: 0.7234 - val_accuracy: 0.8125
Epoch 2/10
...

✅ Training completed!
📊 Calculating metrics...
📈 Overall Metrics:
   Accuracy:  92.45%
   Recall:    91.23%

💾 Saving artifacts...
✅ Model saved to: blood_cell_model.keras
✅ Class names saved
✅ Metrics saved

🎉 Training Complete!
```

---

## Troubleshooting

**Error: "Training directory not found"**
- Check path in `train.py` line 21: `TRAIN_DIR`
- Make sure lowercase: `C:\Users\ADMIN\OneDrive\Desktop\train`

**Error: "No images found"**
- Your train folder should have subfolders (one per class)
- Each subfolder should contain images

**Training too slow?**
- Reduce `EPOCHS` from 10 to 5
- The model will be less accurate but train faster

**Want better accuracy?**
- Increase `EPOCHS` to 15-20
- Add more training images
- Will take longer to train

---

##Ready to Start Training?

```bash
python train.py
```

Let the model train, then your Blood Sense AI will be fully operational! 🚀
