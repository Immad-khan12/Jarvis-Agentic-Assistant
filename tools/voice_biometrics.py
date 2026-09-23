import os
import numpy as np
import librosa
from scipy.spatial.distance import cosine

VOICEPRINT_FILE = "owner_voiceprint.npy"

def extract_features(audio_path: str):
    """Extracts MFCC audio features from input voice sample."""
    y, sr = librosa.load(audio_path, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    return np.mean(mfcc.T, axis=0)

def register_owner_voice(sample_audio_path: str):
    """Saves the owner's permanent MFCC voiceprint."""
    features = extract_features(sample_audio_path)
    np.save(VOICEPRINT_FILE, features)
    print("✅ Owner Voiceprint saved as 'owner_voiceprint.npy'.")

def verify_speaker(audio_path: str, threshold: float = 0.32) -> bool:
    """Compares incoming voice sample with registered owner voiceprint."""
    if not os.path.exists(VOICEPRINT_FILE):
        print("⚠️ Voiceprint missing. Allowing password unlock by default.")
        return True

    if not os.path.exists(audio_path):
        print("⚠️ Input audio sample missing. Access denied.")
        return False

    try:
        owner_features = np.load(VOICEPRINT_FILE)
        test_features = extract_features(audio_path)
        distance = cosine(owner_features, test_features)
        print(f"🎙️ [VOICE BIOMETRICS]: Distance = {distance:.4f} (Threshold = {threshold})")

        return distance <= threshold
    except Exception as e:
        print(f"❌ Biometrics Error: {str(e)}")
        return False