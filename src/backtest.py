import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

FEATURES_PATH = "data/processed/features.parquet"
REPORT_PATH = "reports/d05_backtest_test.csv"
FEE_RATE = 0.0010  # 0.10% par changement de position


def compute_performance_metrics(daily_returns: np.ndarray, periods_per_year: int = 252) -> dict:
    """Calcule rendement cumulé, volatilité annualisée, Sharpe Ratio et Max Drawdown."""
    cum_return = np.exp(np.sum(daily_returns)) - 1.0
    ann_return = np.mean(daily_returns) * periods_per_year
    ann_vol = np.std(daily_returns, ddof=1) * np.sqrt(periods_per_year)
    sharpe = (ann_return / ann_vol) if ann_vol > 0 else 0.0

    wealth = np.exp(np.cumsum(daily_returns))
    running_max = np.maximum.accumulate(wealth)
    drawdown = (wealth - running_max) / running_max
    max_dd = np.min(drawdown)  # Valeur négative (ex: -0.12 = -12%)

    return {
        "Rendement Cumulé": cum_return,
        "Rendement Annualisé": ann_return,
        "Volatilité Annualisée": ann_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd,
    }


def simulate_strategy(returns: np.ndarray, signals: np.ndarray, fee_rate: float = FEE_RATE) -> np.ndarray:
    """
    Simule une stratégie long/flat avec frais de transaction proportionnels au turnover.
    signals[t] est décidé à t-1 et appliqué au rendement returns[t] (pas de look-ahead bias).
    """
    pos = np.asarray(signals, dtype=float)
    pos_prev = np.roll(pos, 1)
    pos_prev[0] = 0.0  # Position initiale nulle en début de période test

    turnover = np.abs(pos - pos_prev)
    costs = turnover * fee_rate
    net_returns = pos * returns - costs
    return net_returns


def run_d05_pipeline():
    if not os.path.exists(FEATURES_PATH):
        raise FileNotFoundError(f"Fichier introuvable : {FEATURES_PATH}")

    df = pd.read_parquet(FEATURES_PATH)
    test_df = df[df["split"] == "test"].copy()

    r_xlf = test_df["r_xlf"].to_numpy()
    r_spy = test_df["r_spy"].to_numpy()

    # Stratégie 1 : Momentum / Trend-following filtré par MA20 (déjà décalée t-1 dans features.parquet)
    # Long (1) si moyenne mobile 20j > 0, sinon Cash/Flat (0)
    sig_ma20 = (test_df["r_xlf_ma20"].to_numpy() > 0).astype(float)
    strat_ma20_ret = simulate_strategy(r_xlf, sig_ma20, fee_rate=FEE_RATE)

    # Stratégie 2 : Contrarian / Mean-Reversion sur choc de marché SPY_{t-1}
    # Si SPY_{t-1} a baissé (< -0.5%), position long (1), sinon flat (0)
    sig_spy_rebound = (test_df["r_spy_lag1"].to_numpy() < -0.005).astype(float)
    strat_rebound_ret = simulate_strategy(r_xlf, sig_spy_rebound, fee_rate=FEE_RATE)

    # Benchmark 1 : Buy & Hold XLF (position 1 constante, 1 seul coût d'entrée au jour 0)
    sig_bh_xlf = np.ones(len(r_xlf))
    bh_xlf_ret = simulate_strategy(r_xlf, sig_bh_xlf, fee_rate=FEE_RATE)

    # Benchmark 2 : Buy & Hold SPY
    sig_bh_spy = np.ones(len(r_spy))
    bh_spy_ret = simulate_strategy(r_spy, sig_bh_spy, fee_rate=FEE_RATE)

    strategies = {
        "Stratégie : Trend MA20 (>0, frais 0.10%)": strat_ma20_ret,
        "Stratégie : Rebond SPY_{t-1} (frais 0.10%)": strat_rebound_ret,
        "Benchmark : Buy & Hold XLF (frais 0.10%)": bh_xlf_ret,
        "Benchmark : Buy & Hold SPY (frais 0.10%)": bh_spy_ret,
    }

    rows = []
    for name, rets in strategies.items():
        m = compute_performance_metrics(rets)
        rows.append({"Stratégie / Benchmark": name, **m})

    bt_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    bt_df.to_csv(REPORT_PATH, index=False)

    print("=" * 65)
    print("LIVRABLE D05 — BACKTEST SUR TEST (2025-2026, FRAIS 0.10%)")
    print("=" * 65)
    print(bt_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nRésultats sauvegardés dans : {REPORT_PATH}")


if __name__ == "__main__":
    run_d05_pipeline()