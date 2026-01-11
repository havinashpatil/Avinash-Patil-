"""
Blood Sense AI - Model Training Script
This script trains the MobileNetV2 model on blood cell images.

NOTE: For systems with limited GPU memory or large datasets, use the
memory-efficient training script instead:
    python train_memory_efficient.py --help

Features of memory-efficient mode:
  - GPU/CPU hybrid training with automatic detection
  - Mixed precision (float16) for faster GPU execution
  - Iterative batch processing to prevent memory overflow
  - Automatic checkpoint saving and early stopping
  - Memory cleanup between batches

See MEMORY_EFFICIENT_TRAINING.md for detailed guide.
"""
import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from sklearn.metrics import classification_report
from datetime import datetime

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TRAIN_DIR = r'C:\Users\ADMIN\OneDrive\Desktop\train'  # Your training dataset

# Output paths
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'blood_cell_model.keras')
CLASS_NAMES_PATH = os.path.join(BASE_DIR, 'class_names.json')
METRICS_PATH = os.path.join(BASE_DIR, 'model_metrics.json')

# Training parameters
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10  # Adjust as needed
LEARNING_RATE = 0.001


def load_dataset(directory):
    """Load dataset from directory"""
    if not os.path.isdir(directory):
        print(f"❌ Directory {directory} does not exist!")
        return None, None
    
    try:
        dataset = image_dataset_from_directory(
            directory,
            labels='inferred',
            label_mode='categorical',
            image_size=IMG_SIZE,
            batch_size=BATCH_SIZE,
            shuffle=True,
            seed=42
        )
        
        class_names = dataset.class_names
        print(f"✅ Found {len(class_names)} classes: {class_names}")
        
        return dataset, class_names
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None, None


def preprocess_dataset(dataset):
    """Apply MobileNetV2 preprocessing"""
    def preprocess(image, label):
        return preprocess_input(image), label
    
    return dataset.map(preprocess, num_parallel_calls=tf.data.AUTOTUNE).prefetch(tf.data.AUTOTUNE)


def build_model(num_classes):
    """Build MobileNetV2 model"""
    print(f"\n🔨 Building model for {num_classes} classes...")
    
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False
    
    # Add custom classification layers
    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))                            
    x = base_model(inputs, training=False)
    x = GlobalAveragePooling2D()(x)
    outputs = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs, outputs)
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Model built successfully")
    model.summary()
    
    return model


def calculate_metrics(model, dataset, class_names):
    """Calculate model performance metrics"""
    print("\n📊 Calculating metrics...")
    
    # Get predictions
    y_pred_probs = model.predict(dataset)
    y_pred_classes = np.argmax(y_pred_probs, axis=1)
    
    # Get true labels
    y_true_one_hot = np.concatenate([y for x, y in dataset], axis=0)
    y_true_classes = np.argmax(y_true_one_hot, axis=1)
    
    # Calculate metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    accuracy = accuracy_score(y_true_classes, y_pred_classes)
    precision = precision_score(y_true_classes, y_pred_classes, average='weighted', zero_division=0)
    recall = recall_score(y_true_classes, y_pred_classes, average='weighted', zero_division=0)
    f1 = f1_score(y_true_classes, y_pred_classes, average='weighted', zero_division=0)
    
    # Per-class metrics
    from sklearn.metrics import classification_report as sklearn_report
    report = sklearn_report(y_true_classes, y_pred_classes, target_names=class_names, 
                           output_dict=True, zero_division=0)
    
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
        'last_trained': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print(f"\n📈 Overall Metrics:")
    print(f"   Accuracy:  {accuracy*100:.2f}%")
    print(f"   Precision: {precision*100:.2f}%")
    print(f"   Recall:    {recall*100:.2f}%")
    print(f"   F1-Score:  {f1*100:.2f}%")
    
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
    """Main training function"""
    print("\n" + "="*60)
    print("🔬 Blood Sense AI - Model Training")
    print("="*60)
    
    # Check training data
    if not os.path.isdir(TRAIN_DIR):
        print(f"\n❌ Training directory not found: {TRAIN_DIR}")
        print("Please check the path and try again.")
        return
    
    # Load training data
    print(f"\n📂 Loading training data from: {TRAIN_DIR}")
    train_ds_raw, class_names = load_dataset(TRAIN_DIR)
    
    if train_ds_raw is None:
        print("❌ Failed to load dataset. Exiting.")
        return
    
    # Split into train and validation (80/20)
    train_size = int(0.8 * len(list(train_ds_raw)))
    train_ds = train_ds_raw.take(train_size)
    val_ds = train_ds_raw.skip(train_size)
    
    print(f"✅ Training batches: {len(list(train_ds))}")
    print(f"✅ Validation batches: {len(list(val_ds))}")
    
    # Preprocess datasets
    print("\n🔄 Preprocessing datasets...")
    train_ds = preprocess_dataset(train_ds).cache()
    val_ds = preprocess_dataset(val_ds).cache()
    
    # Build model
    model = build_model(num_classes=len(class_names))
    
    # Train model
    print(f"\n🚀 Starting training for {EPOCHS} epochs...")
    print("="*60)
    
    history = model.fit(
        train_ds,
        epochs=EPOCHS,
        validation_data=val_ds,
        verbose=1
    )
    
    print("="*60)
    print("✅ Training completed!")
    
    # Calculate metrics
    metrics = calculate_metrics(model, val_ds, class_names)
    
    # Save everything
    save_artifacts(model, class_names, metrics)
    
    print("\n" + "="*60)
    print("🎉 Training Complete!")
    print("="*60)
    print(f"\n✅ Model file: {MODEL_SAVE_PATH}")
    print(f"✅ Ready for predictions!")
    print("\nYou can now:")
    print("  1. Test the model: python model.py")
    print("  2. Use the backend API for predictions")
    print("  3. Upload images via the web interface")


if __name__ == '__main__':
    main()
