import pandas as pd


def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df


def dataframe_summary(df):
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "shape": df.shape
    }