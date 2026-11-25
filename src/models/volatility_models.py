import os
import warnings
import numpy as np
import pandas as pd
from scipy.stats import norm
from arch import arch_model

warnings.filterwarnings("ignore")

FEATURES_PATH = "data/processed/features.parquet"
REPORT_PATH = "reports/d04_risk_summary.csv"


def compute_var_es_normal(mean_pred: np.ndarray, sigma_pred: np.ndarray, alpha: float = 0.01):
    """
    Calcule la Value at Risk (VaR) et l'Expected Shortfall (ES) sous hypothèse Normale.
    VaR_alpha est exprimée en perte positive (ex: 0.02 = perte de 2%).
    """
    z_alpha = norm.ppf(alpha)  # -2.3263 pour alpha = 1% (VaR 99%)
    pdf_z = norm.pdf(z_alpha)

    var_loss = -(mean_pred + sigma_pred * z_alpha)
    es_loss = -(mean_pred - sigma_pred * (pdf_z / alpha))
    return var_loss, es_loss


def run_d04_pipeline():
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"Fichier introuvable : {FEATURES_PATH}")

    df = pd.read_parquet(FEATURES_PATH)
    train_df = df[df["split"] == "train"].copy()
    val_df = df[df["split"] == "val"].copy()

    # Mise à l'échelle en pourcentage (%) pour la stabilité numérique de GARCH
    train_r_pct = train_df["r_xlf"].to_numpy() * 100.0
    val_r_pct = val_df["r_xlf"].to_numpy() * 100.0
    val_r = val_df["r_xlf"].to_numpy()

    # 1. Calibration GARCH(1,1) uniquement sur Train (2018-2022)
    am = arch_model(train_r_pct, mean="Constant", vol="GARCH", p=1, q=1, dist="normal")
    res = am.fit(disp="off")

    print("=" * 65)
    print("LIVRABLE D04 — CALIBRATION GARCH(1,1) SUR TRAIN (2018-2022)")
    print("=" * 65)
    print(res.summary().tables[1])

    # 2. Prévision de volatilité hors échantillon sur Validation (2023-2024) sans refit
    full_r_pct = np.concatenate([train_r_pct, val_r_pct])
    full_am = arch_model(full_r_pct, mean="Constant", vol="GARCH", p=1, q=1, dist="normal")
    # Fixation des paramètres estimés sur Train uniquement (zéro fuite du futur)
    fixed_res = full_am.fix(res.params)
    cond_var_pct2 = fixed_res.conditional_volatility[len(train_r_pct):] ** 2
    val_sigma = np.sqrt(cond_var_pct2) / 100.0  # Retour en décimal journalier
    val_mu = np.full_like(val_sigma, res.params["mu"] / 100.0)

    # 3. VaR 99% et Expected Shortfall (ES 99%)
    var99, es99 = compute_var_es_normal(val_mu, val_sigma, alpha=0.01)

    # 4. Backtest statistique simple de la VaR 99% (taux de dépassement / exceptions)
    # Une exception a lieu lorsque le rendement réel est inférieur à -VaR99 (perte > VaR99)
    exceptions = val_r < (-var99)
    emp_exception_rate = np.mean(exceptions) * 100.0

    # Benchmark : volatilité historique glissante 20 jours décalée d'un jour (shift(1))
    rolling_sigma = val_df["r_xlf"].rolling(20).std().shift(1).bfill().to_numpy()
    var99_roll, es99_roll = compute_var_es_normal(np.zeros_like(rolling_sigma), rolling_sigma, alpha=0.01)
    exc_roll = val_r < (-var99_roll)

    summary_df = pd.DataFrame([
        {
            "Modèle Risque": "GARCH(1,1) Normal",
            "Volatilité Moyenne Val": np.mean(val_sigma),
            "VaR 99% Moyenne (perte)": np.mean(var99),
            "ES 99% Moyenne (perte)": np.mean(es99),
            "Exceptions VaR 99% (%)": emp_exception_rate,
            "Cible Théorique (%)": 1.0,
        },
        {
            "Modèle Risque": "Benchmark : Rolling Vol 20j",
            "Volatilité Moyenne Val": np.mean(rolling_sigma),
            "VaR 99% Moyenne (perte)": np.mean(var99_roll),
            "ES 99% Moyenne (perte)": np.mean(es99_roll),
            "Exceptions VaR 99% (%)": np.mean(exc_roll) * 100.0,
            "Cible Théorique (%)": 1.0,
        },
    ])

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    summary_df.to_csv(REPORT_PATH, index=False)

    print("\n" + "=" * 65)
    print("SYNTHÈSE RISQUE SUR VALIDATION (2023-2024)")
    print("=" * 65)
    print(summary_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print(f"\nRésumé sauvegardé dans : {REPORT_PATH}")


if __name__ == "__main__":
    run_d04_pipeline()