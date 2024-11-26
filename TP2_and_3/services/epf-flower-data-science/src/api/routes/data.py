from fastapi import APIRouter, HTTPException
import kagglehub
from pathlib import Path
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

router = APIRouter()
DATA_PATH = Path("src/data")
DATASET_NAME = "iris.csv"
DATASET_PATH = DATA_PATH / DATASET_NAME
KAGGLE_CREDENTIALS = Path("src/config/kaggle.json")

@router.get("/datasets/{name}", tags=["Datasets"])
async def download_dataset(name: str):
    """
    Download a dataset from Kaggle using kagglehub and store it in the src/data directory.
    The name parameter should match Kaggle's dataset identifier (e.g., uciml/iris).
    """
    if not KAGGLE_CREDENTIALS.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"Kaggle credentials not found. Place kaggle.json at {KAGGLE_CREDENTIALS}."
        )
    
    os.environ["KAGGLE_CONFIG_DIR"] = str(KAGGLE_CREDENTIALS.parent)
    DATA_PATH.mkdir(parents=True, exist_ok=True)

    try:
        dataset_path = kagglehub.dataset_download(name, path=str(DATA_PATH))
        return {
            "message": f"Dataset '{name}' downloaded successfully.",
            "files": [str(file) for file in dataset_path.iterdir()]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download dataset: {str(e)}"
        )

@router.get("/load-iris", tags=["Datasets"])
async def load_iris_dataset():
    """
    Load the Iris dataset as a pandas DataFrame and return it as a JSON response.
    """
    # Check if the Iris dataset file exists
    if not DATASET_PATH.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{DATASET_NAME}' not found. Please download it first."
        )

    try:
        df = pd.read_csv(DATASET_PATH)
        return df.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries (JSON format)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading dataset: {str(e)}"
        )


@router.get("/preprocess-iris", tags=["Datasets"])
async def preprocess_iris_data():
    """
    Preprocess the Iris dataset (standardize features, encode labels, and split the dataset into training and test sets).
    """
    dataset_path = DATA_PATH / DATASET_NAME

    # Check if the Iris dataset file exists
    if not dataset_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{DATASET_NAME}' not found. Please download it first."
        )

    try:
        # Load the dataset as a pandas DataFrame
        df = pd.read_csv(dataset_path)

        # Separate features (X) and target variable (y)
        X = df.drop("species", axis=1)  # Features: sepal_length, sepal_width, petal_length, petal_width
        y = df["species"]  # Target: species

        # Encode the target variable (species)
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Split the data into training and testing sets (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

        # Return the preprocessed data as JSON
        return {
            "message": "Data preprocessed successfully.",
            "train_data": {
                "features": X_train.tolist(),
                "labels": y_train.tolist()
            },
            "test_data": {
                "features": X_test.tolist(),
                "labels": y_test.tolist()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error preprocessing dataset: {str(e)}"
        )