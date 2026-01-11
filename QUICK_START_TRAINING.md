# Quick Start: Memory-Efficient Training

## For Users Experiencing Memory Issues

If you're getting out-of-memory errors or crashes during training, use this command:

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run memory-efficient training
python train_memory_efficient.py
```

## Key Features

✅ **Automatic GPU Detection** - Uses GPU if available, falls back to CPU  
✅ **Memory Management** - Prevents overflow with iterative batch processing  
✅ **Mixed Precision** - 2-3x faster training on GPUs  
✅ **Checkpoints** - Saves progress automatically  
✅ **Early Stopping** - Stops when model stops improving  

## Common Commands

### Standard Training (recommended if no memory issues)
```bash
python train_memory_efficient.py --epochs 10 --batch-size 16
```

### Low Memory Systems (reduce batch size)
```bash
python train_memory_efficient.py --epochs 10 --batch-size 8
```

### CPU-Only Training (no GPU)
```bash
python train_memory_efficient.py --disable-mixed-precision
```

### Extended Training (better accuracy)
```bash
python train_memory_efficient.py --epochs 20 --batch-size 16
```

## What It Does

1. **Detects your hardware** (GPU/CPU)
2. **Loads data in chunks** (prevents memory overflow)
3. **Trains the model** with automatic memory cleanup
4. **Saves checkpoints** every time it improves
5. **Stops early** if validation doesn't improve (saves time)
6. **Outputs trained model** ready for predictions

## Output Files

- `blood_cell_model.keras` - Your trained model
- `class_names.json` - Cell type classes
- `model_metrics.json` - Performance metrics
- `checkpoints/` - Backup models

## Troubleshooting

**Still getting memory errors?**
```bash
python train_memory_efficient.py --batch-size 4
```

**Training too slow?**
- Check if GPU is detected (you should see "Available GPUs: 1")
- Install CUDA for GPU acceleration
- Use smaller dataset for testing

**Need help?**
- See full guide: `MEMORY_EFFICIENT_TRAINING.md`
- Compare standard vs memory-efficient training modes
- Check your dataset structure

## Next Steps After Training

```bash
# Test the model
python model.py

# Start the backend API
cd backend
python app.py

# Open frontend (in new terminal)
cd frontend
npm start
```

---

For complete documentation, see [MEMORY_EFFICIENT_TRAINING.md](file:///c:/Users/ADMIN/OneDrive/Desktop/BloodCancerCellDetectAIModel/MEMORY_EFFICIENT_TRAINING.md)
