"""Public, non-PII training data in the format Built-in XGBoost expects."""

import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

LABEL_COLUMN = "label"
VALIDATION_FRACTION = 0.2
DEFAULT_SEED = 42


def load_dataset() -> pd.DataFrame:
    """scikit-learn's breast cancer dataset with the binary label as the first column."""
    bunch = load_breast_cancer(as_frame=True)
    features: pd.DataFrame = bunch.data
    return pd.concat([bunch.target.rename(LABEL_COLUMN), features], axis=1)


def split(frame: pd.DataFrame, seed: int = DEFAULT_SEED) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Stratified train/validation split; the same seed always yields the same split."""
    train, validation = train_test_split(
        frame,
        test_size=VALIDATION_FRACTION,
        random_state=seed,
        stratify=frame[LABEL_COLUMN],
    )
    return train, validation


def to_xgboost_csv(frame: pd.DataFrame) -> str:
    """CSV with the label in column 0, no header and no index, as Built-in XGBoost requires."""
    return str(frame.to_csv(header=False, index=False))
