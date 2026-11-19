# QUANT LAB — Projet Intégrateur : Trading Intelligent

**Édition : Novembre 2026**  
**Département d'Informatique — Faculté des Sciences, Université Mohammed V, Rabat**  
**Responsable Pédagogique :** Pr. Tawfik Masrour

---

## 1. Identification du Binôme & Variante

- **Binôme :**
  - **Étudiant 1 :** [Abid Abderrahmane] — N° Apogée : [21003567]
  - **Étudiant 2 :** [Ayoub Abdedaim] — N° Apogée : [20005069]
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
       |  Contrôles intégrité (OHLCV, horodatage, rendements log)    |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                   02. MODEL LABORATORY                      |
       |  Baselines (Naïf, MM) | Économétrie (ARIMA vs SARIMAX SPY)  |
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
       |  Règle décisionnelle: Signal de moyenne filtré par le risque|
       |  Dimensionnement de position (Position Sizing & Cash)       |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                      05. BACKTESTING                        |
       |  Simulation nette (frais 0.05% + slippage 0.05% = 0.10%)    |
       |  Courbe de richesse | Drawdown max | Sharpe | Buy & Hold    |
       +------------------------------+------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                    06. PAPER TRADING                        |
       |  Simulation sur 5 séances réelles out-of-sample             |
       |  Journal de bord exportable | Mode DEMO hors-ligne          |
       +-------------------------------------------------------------+
```

## 📊 Benchmarks de Référence

Pour évaluer objectivement la valeur ajoutée de notre approche (Variante B03 : **XLF** conditionné par **$SPY_{t-1}$**), nos résultats sont systématiquement comparés à trois niveaux de benchmarks :

1. **Benchmark de Marché :**
   * **SPY (S&P 500 ETF)** : Indice de référence macroéconomique du marché américain.
   * **Buy-and-Hold (XLF)** : Stratégie passive d'achat et de conservation sur l'ETF XLF, servant de référence minimale pour le backtesting (net de frais de 0,10 %).
2. **Benchmarks de Modèles (Baselines - D03) :**
   * **Modèle Naïf (Persistance / Marche aléatoire)** : $\hat{r}_t = r_{t-1}$ et $\hat{r}_t = 0$.
   * **Moyenne Mobile (Rolling Mean)** : Prévision basée sur la moyenne glissante des rendements passés (fenêtres de 5 et 20 jours).
   * **ARIMA (Univarié sur XLF)** : Modèle autonome servant de référence directe pour mesurer l'apport réel de la variable exogène $SPY_{t-1}$ dans **SARIMAX**.
3. **Critères de Comparaison :**
   * **Statistiques / Prévision** : AIC, BIC, RMSE hors échantillon (*out-of-sample*), test de Ljung-Box sur les résidus.
   * **Financiers / Risque** : Rendement cumulé, Ratio de Sharpe, Maximum Drawdown, VaR (99 %) et Expected Shortfall (ES).

---

## 👥 Répartition des Tâches (Projet Complet)

Le travail est réparti de manière équilibrée sur l'ensemble du cycle de vie du projet (Livrables D01 à D06), avec un suivi collaboratif via Git/GitHub (branches dédiées et Pull Requests) :

| Phase / Livrable | Abderrahmane Abid | Ayoub Abdedaim |
| :--- | :--- | :--- |
| **D01 : Cadrage & Git** | Initialisation du repo, arborescence officielle, `requirements.txt`, documentation `README.md`. | Validation du cadrage B03, configuration de l'environnement, gestion des branches Git. |
| **D02 : Données & Audit** | Script d'ingestion `src/data.py` (`yfinance`, snapshot Parquet, gestion réseau) et `asserts` de qualité. | Feature engineering `src/features.py` (Log Returns, décalage $SPY_{t-1}$ sans look-ahead bias) et `data/README.md`. |
| **D03 : Modèles de Moyenne** | Tests de stationnarité (ADF/KPSS), implémentation des Baselines (Naïf, Moyenne Mobile). | Calibration **ARIMA** vs **SARIMAX ($SPY_{t-1}$)**, évaluation AIC/BIC/RMSE et diagnostic Ljung-Box. |
| **D04 : Risque & Volatilité** | Modélisation **GARCH(1,1)** sur les résidus et détection du *Volatility Clustering*. | Calcul et backtesting de la **VaR (99 %)** et de l'**Expected Shortfall (ES)**. |
| **D05 : Stratégie & Backtest** | Règles de décision (Signaux Achat/Cash combinant SARIMAX + GARCH) et moteur de Backtesting (frais 0,10 %). | Comparaison vs *Buy-and-Hold*, métriques de performance (Sharpe, Drawdown) et module **Paper Trading**. |
| **D06 : App Streamlit & Soutenance** | Intégration des modules `01-Market Data`, `03-Risk Management` et `05-Backtesting` dans Streamlit. | Intégration des modules `02-Model Lab`, `04-Trading Strategy` et `06-Paper Trading`, rapport final. |

---

## 🤖 Transparence & Usage des LLMs

Dans une démarche de transparence académique, nous documentons l'assistance d'outils d'IA générative utilisés au cours du projet :

* **Modèle utilisé :** **Gemini** (Google).
* **Périmètre d'utilisation :**
  * Vulgarisation et approfondissement des concepts théoriques du cours (stationnarité, ARIMA/SARIMAX, GARCH, look-ahead bias).
  * Aide à la structuration modulaire du code Python et au débogage technique (gestion des timeouts réseau `yfinance`, configuration d'environnement Windows/VS Code).
  * Assistance à la structuration de la documentation (`README.md`) et préparation des supports de suivi.
* **Validation humaine :** L'ensemble du code exécuté, les choix d'hyperparamètres, les tests statistiques, ainsi que l'interprétation financière des résultats sont intégralement vérifiés, testés et assumés par le binôme.
