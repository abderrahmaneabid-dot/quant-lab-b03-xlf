import os
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox

warnings.filterwarnings("ignore")

FEATURES_PATH = "data/processed/features.parquet"
REPORT_PATH = "reports/d03_model_comparison.csv"


def run_stationarity_tests(train_df: pd.DataFrame) -> pd.DataFrame:
    """
    Exécute les tests ADF (H0: non-stationnaire) et KPSS (H0: stationnaire)
    sur les prix bruts vs rendements logarithmiques (uniquement sur Train).
    """
    results = []
    for col, label in [("close_xlf", "Prix brut XLF"), ("r_xlf", "Log Return XLF")]:
        series = train_df[col].dropna()
        adf_stat, adf_p, *_ = adfuller(series, autolag="AIC")
        kpss_stat, kpss_p, *_ = kpss(series, regression="c", nlags="auto")

        verdict = "Stationnaire I(0)" if (adf_p < 0.05 and kpss_p > 0.05) else "Non-stationnaire"
        results.append({
            "Série": label,
            "ADF Stat": round(adf_stat, 4),
            "ADF p-value": round(adf_p, 4),
            "KPSS Stat": round(kpss_stat, 4),
            "KPSS p-value": round(kpss_p, 4),
            "Verdict": verdict,
        })
    return pd.DataFrame(results)


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calcule RMSE, MAE et Directional Accuracy (précision du signe)."""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    # Précision directionnelle (en %) sur les jours non nuls
    dir_acc = np.mean(np.sign(y_true) == np.sign(y_pred)) * 100
    return {"RMSE (Val)": rmse, "MAE (Val)": mae, "Dir Acc (%)": dir_acc}


def select_best_sarimax(train_y: np.ndarray, train_x: np.ndarray = None, max_p: int = 2, max_q: int = 2):
    """
    Sélectionne le meilleur ordre (p, 0, q) par minimisation de l'AIC sur Train.
    """
    best_aic = np.inf
    best_order = None
    best_res = None

    for p in range(max_p + 1):
        for q in range(max_q + 1):
            if p == 0 and q == 0 and train_x is None:
                continue
            try:
                model = SARIMAX(
                    train_y,
                    exog=train_x,
                    order=(p, 0, q),
                    trend="c",
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                res = model.fit(disp=False)
                if res.aic < best_aic:
                    best_aic = res.aic
                    best_order = (p, 0, q)
                    best_res = res
            except Exception:
                continue

    return best_order, best_res


def run_d03_pipeline():
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"Fichier introuvable : {FEATURES_PATH}. Lancez src/features.py d'abord.")

    df = pd.read_parquet(FEATURES_PATH)
    train_df = df[df["split"] == "train"]
    val_df = df[df["split"] == "val"]

    print("=" * 65)
    print("1. TESTS DE STATIONNARITÉ (SUR TRAIN : 2018-2022)")
    print("=" * 65)
    stat_table = run_stationarity_tests(train_df)
    print(stat_table.to_string(index=False))

    # Préparation des séries cibles et exogènes
    train_y = train_df["r_xlf"].to_numpy()
    val_y = val_df["r_xlf"].to_numpy()
    train_x = train_df[["r_spy_lag1"]].to_numpy()
    val_x = val_df[["r_spy_lag1"]].to_numpy()

    rows = []

    # 2. Baselines (Benchmarks de modèles sur Validation)
    baselines = {
        "Baseline : Naïf Zéro (r_t = 0)": np.zeros(len(val_y)),
        "Baseline : Naïf Persistance (r_{t-1})": val_df["r_xlf_lag1"].to_numpy(),
        "Baseline : Moyenne Mobile 5j": val_df["r_xlf_ma5"].to_numpy(),
        "Baseline : Moyenne Mobile 20j": val_df["r_xlf_ma20"].to_numpy(),
    }

    for name, preds in baselines.items():
        metrics = evaluate_predictions(val_y, preds)
        rows.append({
            "Modèle": name,
            "Ordre": "-",
            "AIC": np.nan,
            "BIC": np.nan,
            "RMSE (Val)": metrics["RMSE (Val)"],
            "MAE (Val)": metrics["MAE (Val)"],
            "Dir Acc (%)": metrics["Dir Acc (%)"],
            "Ljung-Box p (lag 10)": np.nan,
            "Ljung-Box p (lag 20)": np.nan,
        })

    # 3. ARIMA (Autonome sur XLF)
    print("\nCalibration ARIMA (autonome sur XLF)...")
    arima_order, arima_res = select_best_sarimax(train_y, train_x=None)
    arima_val_res = arima_res.append(val_y, refit=False)
    arima_preds = arima_val_res.get_prediction(
        start=len(train_y), end=len(train_y) + len(val_y) - 1
    ).predicted_mean
    arima_metrics = evaluate_predictions(val_y, arima_preds)
    lb_arima = acorr_ljungbox(arima_res.resid, lags=[10, 20], return_df=True)

    rows.append({
        "Modèle": "ARIMA (XLF seul)",
        "Ordre": str(arima_order),
        "AIC": arima_res.aic,
        "BIC": arima_res.bic,
        "RMSE (Val)": arima_metrics["RMSE (Val)"],
        "MAE (Val)": arima_metrics["MAE (Val)"],
        "Dir Acc (%)": arima_metrics["Dir Acc (%)"],
        "Ljung-Box p (lag 10)": lb_arima.loc[10, "lb_pvalue"],
        "Ljung-Box p (lag 20)": lb_arima.loc[20, "lb_pvalue"],
    })

    # 4. SARIMAX (Conditionné par SPY_{t-1} — Variante B03)
    print("Calibration SARIMAX (XLF conditionné par SPY_{t-1})...")
    sarimax_order, sarimax_res = select_best_sarimax(train_y, train_x=train_x)
    sarimax_val_res = sarimax_res.append(val_y, exog=val_x, refit=False)
    sarimax_preds = sarimax_val_res.get_prediction(
        start=len(train_y), end=len(train_y) + len(val_y) - 1
    ).predicted_mean
    sarimax_metrics = evaluate_predictions(val_y, sarimax_preds)
    lb_sarimax = acorr_ljungbox(sarimax_res.resid, lags=[10, 20], return_df=True)

    rows.append({
        "Modèle": "SARIMAX (XLF + SPY_{t-1})",
        "Ordre": str(sarimax_order),
        "AIC": sarimax_res.aic,
        "BIC": sarimax_res.bic,
        "RMSE (Val)": sarimax_metrics["RMSE (Val)"],
        "MAE (Val)": sarimax_metrics["MAE (Val)"],
        "Dir Acc (%)": sarimax_metrics["Dir Acc (%)"],
        "Ljung-Box p (lag 10)": lb_sarimax.loc[10, "lb_pvalue"],
        "Ljung-Box p (lag 20)": lb_sarimax.loc[20, "lb_pvalue"],
    })

    # Synthèse & Sauvegarde
    comp_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    comp_df.to_csv(REPORT_PATH, index=False)

    print("\n" + "=" * 65)
    print("2. TABLEAU COMPARATIF DES MODÈLES (VALIDATION : 2023-2024)")
    print("=" * 65)
    print(comp_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))

    # Affichage de la significativité du coefficient exogène SPY_{t-1}
    print("\n" + "=" * 65)
    print("3. SIGNIFICATIVITÉ DE LA VARIABLE EXOGÈNE SPY_{t-1} (SARIMAX)")
    print("=" * 65)
    print(f"Coefficient x1 (r_spy_lag1) : {sarimax_res.params[1]:.6f}")
    print(f"p-value x1 (r_spy_lag1)     : {sarimax_res.pvalues[1]:.6f}")
    print(f"\nTableau sauvegardé dans : {REPORT_PATH}")


if __name__ == "__main__":
    run_d03_pipeline()