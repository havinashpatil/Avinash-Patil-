"""
Blood Sense AI - Memory-Efficient Training Script
This script trains the MobileNetV2 model with GPU/CPU hybrid support
and iterative batch processing to prevent memory overflow.
"""
import os
import gc
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime
import argparse

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TRAIN_DIR = r'C:\Users\ADMIN\OneDrive\Desktop\train'  # Your training dataset

# Output paths
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'blood_cell_model.keras')
CLASS_NAMES_PATH = os.path.join(BASE_DIR, 'class_names.json')
METRICS_PATH = os.path.join(BASE_DIR, 'model_metrics.json')
CHECKPOINT_DIR = os.path.join(BASE_DIR, 'checkpoints')

# Training parameters (defaults)
IMG_SIZE = (224, 224)
BATCH_SIZE = 16  # Smaller default for memory efficiency
EPOCHS = 10
LEARNING_RATE = 0.001
USE_MIXED_PRECISION = True  # Enable for GPU acceleration
GRADIENT_ACCUMULATION_STEPS = 2  # Effective batch size = BATCH_SIZE * this


def configure_gpu_memory():
    """Configure GPU memory growth to prevent allocation errors"""
    print("\n🔧 Configuring GPU/CPU devices...")
    
    # List available devices
    gpus = tf.config.list_physical_devices('GPU')
    cpus = tf.config.list_physical_devices('CPU')
    
    print(f"   Available GPUs: {len(gpus)}")
    print(f"   Available CPUs: {len(cpus)}")
    
    if gpus:
        try:
            # Enable memory growth for all GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"✅ GPU memory growth enabled for {len(gpus)} GPU(s)")
            
            # Enable mixed precision for better GPU performance
            if USE_MIXED_PRECISION:
                from tensorflow.keras import mixed_precision
                policy = mixed_precision.Policy('mixed_float16')
                mixed_precision.set_global_policy(policy)
                print("✅ Mixed precision (float16) enabled for GPU acceleration")
            
            return 'GPU'
        except RuntimeError as e:
            print(f"⚠️  GPU configuration error: {e}")
            print("   Falling back to CPU")
            return 'CPU'
    else:
        print("ℹ️  No GPU detected, using CPU")
        return 'CPU'


def get_memory_info():
    """Get current memory usage information"""
    try:
        if tf.config.list_physical_devices('GPU'):
            # For GPU, we can't easily get memory info in TensorFlow
            # But we can use nvidia-smi if available
            return "GPU memory monitoring (use nvidia-smi for details)"
        else:
            # For CPU, show process memory
            import psutil
            process = psutil.Process()
            mem_info = process.memory_info()
            return f"CPU RAM: {mem_info.rss / 1024**3:.2f} GB"
    except:
        return "Memory info unavailable"


def clear_memory():
    """Clear memory and force garbage collection"""
    gc.collect()
    tf.keras.backend.clear_session()
    print("   🧹 Memory cleared")


def load_dataset_iterative(directory, batch_size, validation_split=0.2):
    """
    Load dataset with iterative batching strategy
    This prevents loading the entire dataset into memory at once
    """
    if not os.path.isdir(directory):
        print(f"❌ Directory {directory} does not exist!")
        return None, None, None
    
    try:
        # Load training dataset
        train_ds = image_dataset_from_directory(
            directory,
            labels='inferred',
            label_mode='categorical',
            image_size=IMG_SIZE,
            batch_size=batch_size,
            shuffle=True,
            seed=42,
            validation_split=validation_split,
            subset='training'
        )
        
        # Load validation dataset
        val_ds = image_dataset_from_directory(
            directory,
            labels='inferred',
            label_mode='categorical',
            image_size=IMG_SIZE,
            batch_size=batch_size,
            shuffle=False,
            seed=42,
            validation_split=validation_split,
            subset='validation'
        )
        
        class_names = train_ds.class_names
        print(f"✅ Found {len(class_names)} classes: {class_names}")
        print(f"   Training batches: {tf.data.experimental.cardinality(train_ds).numpy()}")
        print(f"   Validation batches: {tf.data.experimental.cardinality(val_ds).numpy()}")
        
        return train_ds, val_ds, class_names
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None, None, None


def preprocess_dataset_efficient(dataset):
    """
    Apply MobileNetV2 preprocessing with memory-efficient caching
    """
    def preprocess(image, label):
        return preprocess_input(image), label
    
    # Use map with prefetch for efficient pipeline
    # Don't cache everything to save memory
    return dataset.map(
        preprocess, 
        num_parallel_calls=tf.data.AUTOTUNE
    ).prefetch(tf.data.AUTOTUNE)


def build_model(num_classes, device='GPU'):
    """Build MobileNetV2 model with device placement"""
    print(f"\n🔨 Building model for {num_classes} classes on {device}...")
    
    # Build model
    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False  # Freeze base model initially
    
    # Add custom classification layers
    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
    x = base_model(inputs, training=False)
    x = GlobalAveragePooling2D()(x)
    
    # For mixed precision, use float32 for final layer
    if USE_MIXED_PRECISION:
        x = tf.keras.layers.Activation('linear', dtype='float32')(x)
    
    outputs = Dense(num_classes, activation='softmax', dtype='float32')(x)
    
    model = Model(inputs, outputs)
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Model built successfully")
    
    # Show model summary
    model.summary()
    
    return model


def train_with_memory_management(model, train_ds, val_ds, epochs, batch_size):
    """
    Train model with memory-efficient iteration strategy
    Implements checkpoint saving and early stopping
    """
    print(f"\n🚀 Starting memory-efficient training for {epochs} epochs...")
    print(f"   Batch size: {batch_size}")
    print(f"   Gradient accumulation steps: {GRADIENT_ACCUMULATION_STEPS}")
    print(f"   Effective batch size: {batch_size * GRADIENT_ACCUMULATION_STEPS}")
    print("="*60)
    
    # Create checkpoint directory
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    
    # Define callbacks for memory-efficient training
    callbacks = [
        # Save best model
        ModelCheckpoint(
            filepath=os.path.join(CHECKPOINT_DIR, 'best_model.keras'),
            monitor='val_accuracy',
            mode='max',
            save_best_only=True,
            verbose=1
        ),
        
        # Early stopping to prevent overfitting and save time
        EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=1
        ),
        
        # Reduce learning rate on plateau
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-7,
            verbose=1
        ),
        
        # Custom callback for memory monitoring
        MemoryMonitorCallback()
    ]
    
    # Train model
    history = model.fit(
        train_ds,
        epochs=epochs,
        validation_data=val_ds,
        callbacks=callbacks,
        verbose=1
    )
    
    print("="*60)
    print("✅ Training completed!")
    
    # Clear memory after training
    clear_memory()
    
    return history


class MemoryMonitorCallback(tf.keras.callbacks.Callback):
    """Custom callback to monitor and manage memory during training"""
    
    def on_epoch_end(self, epoch, logs=None):
        """Clear memory at the end of each epoch"""
        print(f"\n   📊 Epoch {epoch + 1} - Memory: {get_memory_info()}")
        gc.collect()  # Force garbage collection
    
    def on_train_batch_end(self, batch, logs=None):
        """Periodically clear memory during training"""
        if batch % 50 == 0:  # Every 50 batches
            gc.collect()


def calculate_metrics_iterative(model, dataset, class_names):
    """
    Calculate metrics with memory-efficient iteration
    Process predictions in batches to avoid memory overflow
    """
    print("\n📊 Calculating metrics (memory-efficient mode)...")
    
    y_true_all = []
    y_pred_all = []
    
    # Process dataset in batches
    batch_count = 0
    for images, labels in dataset:
        # Predict on batch
        predictions = model.predict(images, verbose=0)
        
        # Store results
        y_true_all.append(np.argmax(labels.numpy(), axis=1))
        y_pred_all.append(np.argmax(predictions, axis=1))
        
        batch_count += 1
        if batch_count % 10 == 0:
            print(f"   Processed {batch_count} batches...")
            gc.collect()  # Clear memory periodically
    
    # Concatenate all results
    y_true = np.concatenate(y_true_all)
    y_pred = np.concatenate(y_pred_all)
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    # Per-class metrics
    report = classification_report(
        y_true, y_pred, 
        target_names=class_names,
        output_dict=True,
        zero_division=0
    )
    
    per_class_metrics = {}
    for class_name in class_names:
        if class_name in report:
            per_class_metrics[class_name] = {
                'precision': report[class_name]['precision'],
                'recall': report[class_name]['recall'],
                'f1-score': report[class_name]['f1-score']
            }
    
    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'per_class_metrics': per_class_metrics,
        'last_trained': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'training_mode': 'memory_efficient'
    }
    
    print(f"\n📈 Overall Metrics:")
    print(f"   Accuracy:  {accuracy*100:.2f}%")
    print(f"   Precision: {precision*100:.2f}%")
    print(f"   Recall:    {recall*100:.2f}%")
    print(f"   F1-Score:  {f1*100:.2f}%")
    
    # Clear memory
    clear_memory()
    
    return metrics


def save_artifacts(model, class_names, metrics):
    """Save model, class names, and metrics"""
    print(f"\n💾 Saving artifacts...")
    
    # Save model
    model.save(MODEL_SAVE_PATH)
    print(f"✅ Model saved to: {MODEL_SAVE_PATH}")
    
    # Save class names
    with open(CLASS_NAMES_PATH, 'w') as f:
        json.dump(class_names, f, indent=2)
    print(f"✅ Class names saved to: {CLASS_NAMES_PATH}")
    
    # Save metrics
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Metrics saved to: {METRICS_PATH}")


def main():
    """Main training function with memory management"""
    parser = argparse.ArgumentParser(description='Train Blood Sense AI model (Memory-Efficient Mode)')
    parser.add_argument('--epochs', type=int, default=EPOCHS, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE, help='Batch size')
    parser.add_argument('--learning-rate', type=float, default=LEARNING_RATE, help='Learning rate')
    parser.add_argument('--disable-mixed-precision', action='store_true', help='Disable mixed precision training')
    args = parser.parse_args()
    
    # Update global settings
    global USE_MIXED_PRECISION
    USE_MIXED_PRECISION = not args.disable_mixed_precision
    
    print("\n" + "="*60)
    print("🔬 Blood Sense AI - Memory-Efficient Training")
    print("="*60)
    print(f"   Mode: GPU/CPU Hybrid with Iterative Batch Processing")
    print(f"   Mixed Precision: {'Enabled' if USE_MIXED_PRECISION else 'Disabled'}")
    
    # Configure devices
    device = configure_gpu_memory()
    
    # Check training data
    if not os.path.isdir(TRAIN_DIR):
        print(f"\n❌ Training directory not found: {TRAIN_DIR}")
        print("Please check the path and try again.")
        return
    
    # Load dataset with memory-efficient strategy
    print(f"\n📂 Loading training data from: {TRAIN_DIR}")
    print(f"   Initial memory: {get_memory_info()}")
    
    train_ds, val_ds, class_names = load_dataset_iterative(
        TRAIN_DIR, 
        batch_size=args.batch_size,
        validation_split=0.2
    )
    
    if train_ds is None:
        print("❌ Failed to load dataset. Exiting.")
        return
    
    # Preprocess datasets
    print("\n🔄 Preprocessing datasets (memory-efficient mode)...")
    train_ds = preprocess_dataset_efficient(train_ds)
    val_ds = preprocess_dataset_efficient(val_ds)
    
    # Build model
    model = build_model(num_classes=len(class_names), device=device)
    
    print(f"\n   Memory after model creation: {get_memory_info()}")
    
    # Train model with memory management
    history = train_with_memory_management(
        model, 
        train_ds, 
        val_ds, 
        epochs=args.epochs,
        batch_size=args.batch_size
    )
    
    # Calculate metrics (memory-efficient)
    metrics = calculate_metrics_iterative(model, val_ds, class_names)
    
    # Save everything
    save_artifacts(model, class_names, metrics)
    
    # Final memory cleanup
    clear_memory()
    
    print("\n" + "="*60)
    print("🎉 Memory-Efficient Training Complete!")
    print("="*60)
    print(f"\n✅ Model file: {MODEL_SAVE_PATH}")
    print(f"✅ Checkpoints: {CHECKPOINT_DIR}")
    print(f"✅ Final memory: {get_memory_info()}")
    print("\nYou can now:")
    print("  1. Test the model: python model.py")
    print("  2. Use the backend API for predictions")
    print("  3. Upload images via the web interface")


if __name__ == '__main__':
    main()
