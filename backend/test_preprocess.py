"""Quick test script to validate preprocessing pipeline."""

from src.data.preprocess import preprocess
import numpy as np

if __name__ == "__main__":
    print("=" * 60)
    print("CropSense Preprocessing Test")
    print("=" * 60)
    
    try:
        # Run preprocessing
        X_train, X_test, y_train, y_test, preprocessor = preprocess()
        
        print(f"\n✓ Data loaded successfully")
        print(f"\nDataset Statistics:")
        print(f"  Training set size: {X_train.shape[0]}")
        print(f"  Test set size: {X_test.shape[0]}")
        print(f"  Number of features: {X_train.shape[1]}")
        
        print(f"\nFeature Statistics (Training set):")
        print(f"  Mean: {X_train.mean(axis=0)}")
        print(f"  Std: {X_train.std(axis=0)}")
        
        print(f"\nTarget Distribution (Training):")
        unique, counts = np.unique(y_train, return_counts=True)
        for crop_id, count in zip(unique, counts):
            crop_name = preprocessor.label_encoder.inverse_transform([crop_id])[0]
            print(f"  {crop_name}: {count} samples")
        
        print(f"\nEncoders saved:")
        print(f"  Scaler: {preprocessor.scaler_save_path}")
        print(f"  Label Encoder: {preprocessor.encoder_save_path}")
        
        print(f"\n✓ Preprocessing completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error during preprocessing: {e}")
        raise
