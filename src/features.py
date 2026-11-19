import os
import numpy as np
import pandas as pd

RAW_PATH = "data/raw/market_data_snapshot.parquet"
PROCESSED_PATH = "data/processed/features.parquet"


def extract_close_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait les prix de clôture ajustés (XLF et SPY) quelle que soit
    la structure MultiIndex retournée par yfinance.
    """
    if isinstance(df.columns, pd.MultiIndex):
        if "Close" in df.columns.get_level_values(0):
            prices = df["Close"][["XLF", "SPY"]].copy()
        else:
            prices = pd.DataFrame({
                "XLF": df["XLF"]["Close"],
                "SPY": df["SPY"]["Close"],
            })
    else:
        prices = df[["XLF", "SPY"]].copy()

    prices.index = pd.to_datetime(prices.index)
    prices = prices.sort_index()
    return prices


def build_features(raw_path: str = RAW_PATH, save_path: str = PROCESSED_PATH) -> pd.DataFrame:
    """
    Calcule les rendements logarithmiques, crée les variables retardées (t-1)
    sans look-ahead bias, et applique le découpage temporel Train / Val / Test.
    """
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Snapshot introuvable : {raw_path}. Exécutez d'abord src/data.py.")

    raw_df = pd.read_parquet(raw_path)
    prices = extract_close_prices(raw_df)

    # Alignement strict sur les jours de cotation communs
    prices = prices.dropna()

    features = pd.DataFrame(index=prices.index)
    features["close_xlf"] = prices["XLF"]
    features["close_spy"] = prices["SPY"]

    # 1. Rendements logarithmiques : r_t = ln(P_t / P_{t-1})
    features["r_xlf"] = np.log(features["close_xlf"] / features["close_xlf"].shift(1))
    features["r_spy"] = np.log(features["close_spy"] / features["close_spy"].shift(1))

    # 2. Variables retardées (t-1) — Zéro Look-Ahead Bias
    features["r_xlf_lag1"] = features["r_xlf"].shift(1)      # Pour le modèle Naïf
    features["r_spy_lag1"] = features["r_spy"].shift(1)      # Variable exogène B03 (SARIMAX)

    # Moyennes mobiles retardées d'un jour (pour les baselines D03)
    features["r_xlf_ma5"] = features["r_xlf"].rolling(window=5).mean().shift(1)
    features["r_xlf_ma20"] = features["r_xlf"].rolling(window=20).mean().shift(1)

    # Suppression des lignes initiales contenant des NaN (dues au lag et rolling 20j)
    features = features.dropna()

    # 3. Découpage chronologique strict (Train / Val / Test)
    features["split"] = "test"
    features.loc[features.index <= "2022-12-31", "split"] = "train"
    features.loc[(features.index >= "2023-01-01") & (features.index <= "2024-12-31"), "split"] = "val"

    # 4. Audits de qualité (Asserts)
    assert not features.isna().any().any(), "Erreur : des valeurs NaN subsistent dans les features !"
    assert np.isfinite(features.select_dtypes(include=[np.number])).all().all(), "Erreur : valeurs infinies détectées !"
    assert features.index.is_monotonic_increasing, "Erreur : l'index temporel n'est pas trié chronologiquement !"
    assert not features.index.duplicated().any(), "Erreur : dates en doublon détectées !"

    # Sauvegarde
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    features.to_parquet(save_path)

    print(f"Features sauvegardées avec succès dans : {save_path}")
    print(f"Dimensions totales : {features.shape}")
    print("\nRépartition chronologique (Train / Val / Test) :")
    print(features["split"].value_counts())

    return features


if __name__ == "__main__":
    df_feat = build_features()
    print("\nAperçu des 5 premières lignes :")
    print(df_feat[["close_xlf", "r_xlf", "r_spy_lag1", "split"]].head())