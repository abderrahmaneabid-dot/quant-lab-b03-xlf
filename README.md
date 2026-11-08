# QUANT LAB — Projet Intégrateur : Trading Intelligent

**Édition : Novembre 2026**  
**Département d'Informatique — Faculté des Sciences, Université Mohammed V, Rabat**  
**Responsable Pédagogique :** Pr. Tawfik Masrour

---

## 1. Identification du Binôme & Variante

- **Binôme :**
  - **Étudiant 1 :** [Abid Abderrahmane] — N° Apogée : [21003567]
  - **Étudiant 2 :** [Ayoub Abdedaim] — N° Apogée : [XXXXXXXX]
- **Variante attribuée :** **B03 — XLF (Financial Select Sector SPDR Fund)**
- **Benchmark commun :** **SPY (SPDR S&P 500 ETF Trust)**
- **Univers d'investissement :** Long / Cash exclusif (Pas de vente à découvert, pas d'effet de levier)
- **Capital virtuel initial :** 100 000 USD

---

## 2. Cadrage Scientifique & Question de Recherche

### Question directrice (Variante B03)

> **« Un modèle conditionné par le marché général améliore-t-il le trading d'un secteur financier ? »**

### Hypothèse testable

L'intégration des rendements retardés du marché général ($SPY_{t-1}$) comme variable explicative exogène dans un modèle autorégressif (SARIMAX) apporte une information prédictive statistiquement et économiquement supérieure par rapport à une modélisation purement autonome des rendements du secteur financier ($XLF$).

### Expérience distinctive

- **Modèle autonome :** ARIMA / SARIMA calibré uniquement sur l'historique des rendements de XLF.
- **Modèle conditionné :** SARIMAX incorporant explicitement les rendements retardés de SPY à $t-1$ (sans fuite temporelle).
- **Angle d'évaluation :** Analyse de la valeur ajoutée de l'information exogène (comparaison RMSE, AIC/BIC, test de Ljung-Box sur résidus, ratio de Sharpe et drawdown net de frais).

---

## 3. Architecture & Diagramme du Système

Le système implémente un parcours séquentiel continu sans biais d'anticipation (_zero look-ahead bias_), visualisable à travers une application Web Streamlit à 6 espaces :

```text
       +-------------------------------------------------------------+
       |                  01. MARKET DATA & AUDIT                    |
       |  Collecte yfinance (XLF & SPY) | Snapshot local Parquet/CSV |
       |  Contrôles intégrité (OHLCV, horodatage, rendements log)   |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                   02. MODEL LABORATORY                      |
       |  Baselines (Naïf, MM) | Économétrie (ARIMA vs SARIMAX SPY) |
       |  Machine Learning (Ridge, RF/Boosting) | Deep Learning (MLP)|
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                    03. RISK MANAGEMENT                      |
       |  Test ARCH-LM | Volatilité GARCH(1,1) conditionnelle        |
       |  Value-at-Risk (VaR 99%) & Expected Shortfall (ES)          |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                   04. TRADING STRATEGY                      |
       |  Règle décisionnelle : Signal de moyenne filtré par le risque|
       |  Dimensionnement de position (Position Sizing & Cash)       |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                      05. BACKTESTING                        |
       |  Simulation nette (frais 0.05% + slippage 0.05% = 0.10%)   |
       |  Courbe de richesse | Drawdown max | Sharpe | Buy & Hold    |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                    06. PAPER TRADING                        |
       |  Simulation sur 5 séances réelles out-of-sample             |
       |  Journal de bord exportable | Mode DEMO hors-ligne         |
       +-------------------------------------------------------------+
```
