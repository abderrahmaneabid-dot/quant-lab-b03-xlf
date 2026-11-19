# Documentation des Données & Audit de Qualité (Livrable D02)

## 1. Provenance et Périmètre

- **Source officielle :** Yahoo Finance (via la bibliothèque Python `yfinance`).
- **Actifs extraits :**
  - **XLF** (_Financial Select Sector SPDR Fund_) : Actif cible de la variante **B03**.
  - **SPY** (_SPDR S&P 500 ETF Trust_) : Benchmark de marché et variable exogène.
- **Période couverte :** Du `2018-01-01` au `2026-10-30`.
- **Fréquence et Fuseau horaire :** Données journalières (_Daily_), calées sur le calendrier de cotation de la Bourse de New York (NYSE / EST).

## 2. Convention d'Ajustement

- **Option utilisée :** `auto_adjust=True`.
- **Justification :** Les prix de clôture utilisés sont les **prix ajustés** (_Adjusted Close_), corrigeant automatiquement les fractionnements d'actions (_splits_) et le versement des dividendes afin d'éviter de fausses discontinuités dans le calcul des rendements.

## 3. Architecture des Fichiers Locaux (Reproductibilité)

- `data/raw/market_data_snapshot.parquet` : Photographie locale brute (OHLCV ajusté) générée par `src/data.py` pour garantir l'exécution hors ligne.
- `data/processed/features.parquet` : Jeu de données finalisé généré par `src/features.py`, contenant :
  - Les rendements logarithmiques : $r_t = \ln(P_t / P_{t-1})$ pour XLF (`r_xlf`) et SPY (`r_spy`).
  - Les variables retardées strictement à $t-1$ (`r_spy_lag1`, `r_xlf_lag1`, `r_xlf_ma5`, `r_xlf_ma20`).

## 4. Prévention du Look-Ahead Bias & Découpage Temporel

- **Décalage exogène :** XLF et SPY clôturant simultanément, toute information du marché général utilisée pour prévoir $XLF_t$ est strictement décalée d'une séance (`shift(1)` $\rightarrow$ $SPY_{t-1}$).
- **Découpage chronologique (sans mélange aléatoire) :**
  - **Train :** `2018-01-01` $\rightarrow$ `2022-12-31`
  - **Validation :** `2023-01-01` $\rightarrow$ `2024-12-31`
  - **Test (Out-of-sample) :** `2025-01-01` $\rightarrow$ `2026-10-30`

## 5. Audits de Qualité Automatisés (`assert`)

Chaque exécution du pipeline vérifie automatiquement :

1. L'absence de DataFrame vide après téléchargement.
2. L'alignement exact des dates communes entre XLF et SPY.
3. L'absence de valeurs manquantes (`NaN`) ou infinies (`Inf`) après calcul des rendements et des décalages.
4. La stricte croissance chronologique de l'index temporel sans aucun doublon.
