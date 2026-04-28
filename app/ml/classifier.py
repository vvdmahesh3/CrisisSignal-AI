"""
CrisisSignal AI — TF-IDF + LinearSVC Classifier
Phase 2.1: Replaces pure keyword matching with a trained ML classifier.

The classifier is trained once (flask train-classifier) and saved to disk.
On each request it loads from cache — inference takes < 5ms.
Falls back to keyword engine if model files are missing.

Usage:
    from app.ml.classifier import CrisisClassifier
    category, ml_confidence = CrisisClassifier.predict("some burning upstairs")
"""

import os
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Model storage location — inside the app/ml/ directory
_MODEL_DIR = Path(__file__).parent
_MODEL_PATH = _MODEL_DIR / "model.pkl"
_VECTORIZER_PATH = _MODEL_DIR / "vectorizer.pkl"

# In-memory cache — loaded once per process
_model = None
_vectorizer = None


def _load_models():
    """Load trained models from disk into memory (once per process)."""
    global _model, _vectorizer
    if _model is not None:
        return True  # Already loaded

    if not _MODEL_PATH.exists() or not _VECTORIZER_PATH.exists():
        logger.warning("[Classifier] Model files not found — run `flask train-classifier`")
        return False

    try:
        _model = joblib.load(_MODEL_PATH)
        _vectorizer = joblib.load(_VECTORIZER_PATH)
        logger.info("[Classifier] TF-IDF + LinearSVC model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"[Classifier] Failed to load model: {e}")
        return False


class CrisisClassifier:
    """TF-IDF + LinearSVC classifier for alert categorisation."""

    @staticmethod
    def is_available():
        """Return True if the trained model is loaded and ready."""
        return _load_models()

    @staticmethod
    def predict(text):
        """
        Classify alert text into a crisis category.

        Returns:
            (category: str, ml_confidence: float 0–1)
            Falls back to ("general", 0.25) if model is unavailable.
        """
        if not _load_models():
            return "general", 0.25

        try:
            features = _vectorizer.transform([text.lower()])
            category = _model.predict(features)[0]

            # Decision function score → normalised confidence
            decision = _model.decision_function(features)
            import numpy as np
            score = float(np.max(decision))
            # Map decision score to [0.0, 1.0] via sigmoid
            ml_confidence = float(1 / (1 + np.exp(-score * 0.5)))
            ml_confidence = round(min(1.0, max(0.25, ml_confidence)), 4)

            return category, ml_confidence
        except Exception as e:
            logger.error(f"[Classifier] Prediction error: {e}")
            return "general", 0.25

    @staticmethod
    def train(save=True):
        """
        Train the TF-IDF + LinearSVC model on built-in training data.
        Call via: flask train-classifier

        Returns: (model, vectorizer, accuracy_score)
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.svm import LinearSVC
        from sklearn.pipeline import Pipeline
        from sklearn.model_selection import cross_val_score
        import numpy as np

        from .training_data import TRAINING_DATA

        texts = [t for t, _ in TRAINING_DATA]
        labels = [l for _, l in TRAINING_DATA]

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),      # Unigrams + bigrams
            max_features=3000,
            sublinear_tf=True,       # Dampens high-frequency terms
            min_df=1,
        )
        model = LinearSVC(
            C=1.0,
            max_iter=1000,
            class_weight="balanced", # Handles imbalanced categories
        )

        X = vectorizer.fit_transform(texts)
        model.fit(X, labels)

        # Cross-validated accuracy
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000,
                                      sublinear_tf=True, min_df=1)),
            ("svc", LinearSVC(C=1.0, max_iter=1000, class_weight="balanced")),
        ])
        scores = cross_val_score(pipeline, texts, labels, cv=min(5, len(set(labels))), scoring="accuracy")
        accuracy = float(np.mean(scores))

        if save:
            joblib.dump(model, _MODEL_PATH)
            joblib.dump(vectorizer, _VECTORIZER_PATH)
            # Reset cache so next prediction loads the new model
            global _model, _vectorizer
            _model = model
            _vectorizer = vectorizer

        return model, vectorizer, accuracy
