# Memory-Efficient Training Guide

This guide explains how to use the memory-efficient training mode for Blood Sense AI, which is designed to handle large datasets and prevent memory overflow errors.

## Overview

The memory-efficient training script (`train_memory_efficient.py`) provides several optimizations:

- **GPU/CPU Hybrid Training**: Automatic device detection with GPU acceleration when available
- **Mixed Precision Training**: Uses float16 for faster GPU computation while maintaining accuracy
- **Iterative Batch Processing**: Processes data in manageable chunks with memory cleanup
- **Gradient Accumulation**: Achieves larger effective batch sizes without memory overhead
- **Checkpoint Management**: Saves progress to resume interrupted training
- **Memory Monitoring**: Tracks memory usage throughout training

## When to Use Memory-Efficient Training

Use this mode when you experience:
- ✅ Out of memory (OOM) errors during training
- ✅ System slowdowns or crashes with standard training
- ✅ Large datasets that don't fit in GPU memory
- ✅ Need to train on systems with limited GPU memory (< 6GB)

Use standard training (`train.py`) when:
- ❌ You have ample GPU memory (8GB+)
- ❌ Working with small datasets
- ❌ Training speed is critical and memory is not a constraint

## Quick Start

### Basic Usage

```bash
# Activate your virtual environment
.venv\Scripts\activate

# Run memory-efficient training with defaults
python train_memory_efficient.py
```

### Custom Configuration

```bash
# Specify training parameters
python train_memory_efficient.py --epochs 15 --batch-size 8 --learning-rate 0.0005

# Disable mixed precision (for CPU-only systems)
python train_memory_efficient.py --disable-mixed-precision
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--epochs` | 10 | Number of training epochs |
| `--batch-size` | 16 | Batch size (reduce if OOM occurs) |
| `--learning-rate` | 0.001 | Learning rate for optimizer |
| `--disable-mixed-precision` | False | Disable float16 mixed precision |

## Memory Optimization Strategies

### 1. Reduce Batch Size

If you encounter memory errors, try reducing the batch size:

```bash
python train_memory_efficient.py --batch-size 8
```

The script uses gradient accumulation, so effective batch size = `batch_size × 2`

### 2. Monitor GPU Memory

**Windows - Task Manager:**
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to Performance tab
3. Select GPU
4. Monitor "Dedicated GPU memory"

**NVIDIA GPUs (if CUDA installed):**
```bash
# Monitor in real-time (updates every second)
nvidia-smi --loop=1
```

### 3. Memory Cleanup

The script automatically:
- Clears memory after each epoch
- Runs garbage collection every 50 batches
- Clears TensorFlow session after training

## GPU vs CPU Training

### GPU Training (Recommended)
- **Automatic Detection**: Script detects NVIDIA GPUs automatically
- **Mixed Precision**: Enabled by default for 2-3x speedup
- **Memory Growth**: Prevents GPU memory allocation errors
- **Typical Speed**: 10-30 seconds per epoch (depends on dataset size)

### CPU Training (Fallback)
- **Automatic Fallback**: Used when no GPU detected
- **Slower Training**: 5-10x slower than GPU
- **No Memory Limits**: Can use system RAM (but slower)
- **Typical Speed**: 2-5 minutes per epoch

## Checkpoint Management

### Automatic Checkpoints

The script saves checkpoints in the `checkpoints/` directory:
- `best_model.keras`: Best model based on validation accuracy
- Automatically restored if training completes early

### Resume Training

If training is interrupted, the script will use the best checkpoint automatically. To manually load:

```python
from tensorflow.keras.models import load_model
model = load_model('checkpoints/best_model.keras')
```

## Advanced Features

### Gradient Accumulation

Simulates larger batch sizes without memory overhead:
- Default: 2 accumulation steps
- Effective batch size = batch_size × 2
- Modify `GRADIENT_ACCUMULATION_STEPS` in the script

### Early Stopping

Training stops early if validation loss doesn't improve for 3 consecutive epochs:
- Saves time and prevents overfitting
- Automatically restores best model weights

### Learning Rate Reduction

Learning rate reduces by 50% when validation loss plateaus:
- Helps find better optima
- Minimum learning rate: 1e-7

## Troubleshooting

### Problem: Out of Memory (OOM) Error

**Solutions:**
1. Reduce batch size: `--batch-size 4`
2. Disable mixed precision: `--disable-mixed-precision`
3. Close other applications using GPU memory
4. Restart your system to clear GPU memory

### Problem: Training is Very Slow

**Solutions:**
1. Check if GPU is being used (should see "Available GPUs: 1")
2. Install CUDA and cuDNN for GPU acceleration
3. Reduce dataset size for testing
4. Use standard `train.py` if you have enough memory

### Problem: CUDA/GPU Not Detected

**Solutions:**
1. Install CUDA Toolkit (11.2 or later)
2. Install cuDNN compatible with your CUDA version
3. Install GPU version of TensorFlow: `pip install tensorflow-gpu`
4. Restart your system after installation

### Problem: Model Quality Issues

**Solutions:**
1. Increase epochs: `--epochs 20`
2. Adjust learning rate: `--learning-rate 0.0001`
3. Check dataset quality and class balance
4. Ensure validation split is representative

## Performance Tips

### For Maximum Speed (with sufficient memory):
```bash
python train_memory_efficient.py --batch-size 32 --epochs 15
```

### For Minimum Memory Usage:
```bash
python train_memory_efficient.py --batch-size 4 --disable-mixed-precision
```

### For Best Accuracy:
```bash
python train_memory_efficient.py --epochs 25 --learning-rate 0.0005 --batch-size 16
```

## Output Files

After training completes, you'll have:

| File | Description |
|------|-------------|
| `blood_cell_model.keras` | Final trained model |
| `class_names.json` | List of cell type classes |
| `model_metrics.json` | Performance metrics (accuracy, precision, recall) |
| `checkpoints/best_model.keras` | Best model during training |

## Monitoring Training Progress

The script displays:
- ✅ GPU/CPU detection and configuration
- 📊 Dataset statistics (batches, classes)
- 🔨 Model architecture summary
- 🚀 Training progress per epoch
- 📈 Validation metrics (loss, accuracy)
- 💾 Checkpoint saves
- 🧹 Memory cleanup notifications

Example output:
```
Epoch 5/10
45/45 [==============================] - 12s - loss: 0.3421 - accuracy: 0.8932 - val_loss: 0.2845 - val_accuracy: 0.9123
📊 Epoch 5 - Memory: GPU memory monitoring (use nvidia-smi for details)
```

## Comparison: Standard vs Memory-Efficient

| Feature | Standard (`train.py`) | Memory-Efficient (`train_memory_efficient.py`) |
|---------|----------------------|-----------------------------------------------|
| Speed | Faster | Slightly slower |
| Memory Usage | Higher | Lower |
| GPU Support | Basic | Advanced (mixed precision) |
| Memory Management | Basic | Comprehensive |
| Checkpoint Saves | No | Yes |
| Early Stopping | No | Yes |
| Best For | Small datasets, powerful GPUs | Large datasets, limited memory |

## Getting Help

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review the console output for error messages
3. Verify your dataset structure matches requirements
4. Ensure dependencies are installed: `pip install -r requirements.txt`

## Example Training Session

```bash
# Complete training workflow

# 1. Activate environment
.venv\Scripts\activate

# 2. Verify dataset location
# Ensure data is in: C:\Users\ADMIN\OneDrive\Desktop\train

# 3. Run training
python train_memory_efficient.py --epochs 10 --batch-size 16

# 4. Monitor progress (look for these indicators)
# ✅ GPU detected
# ✅ Model loaded
# 🚀 Training started
# 📊 Epoch metrics
# ✅ Training completed

# 5. Test the model
python model.py

# 6. Use in application
# Start backend: cd backend && python app.py
```

## Next Steps

After successful training:
1. Test predictions with `python model.py`
2. Review metrics in `model_metrics.json`
3. Start the backend API to use the model
4. Upload test images via the web interface
5. Monitor prediction quality with real data
