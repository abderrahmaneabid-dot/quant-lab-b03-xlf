````markdown
# Livrable D05 — Backtesting & Évaluation de Stratégies (Variante B03 : XLF / SPY)

**Période d'évaluation :** `Test` (`2025–2026`, 458 séances — exécution unique hors échantillon)  
**Frais de transaction :** `0,10 %` (`0.0010`) par changement de position  
**Script :** `src/backtest.py`  
**Rapport généré :** `reports/d05_backtest_test.csv`

---

## 1. Objectif du Livrable D05

Évaluer la performance financière nette de frais (`0,10 %`) de règles de décision systématiques sur `XLF` en utilisant l'échantillon de **Test (`2025–2026`)**, resté strictement isolé durant les phases D02–D04, face aux benchmarks passifs (**Buy & Hold XLF** et **Buy & Hold SPY**).

---

## 2. Règles de Décision & Frais de Transaction

- **Absence de _look-ahead bias_ :** Chaque signal à la date $t$ repose uniquement sur des variables connues à $t-1$ (`r_xlf_ma20` ou `r_spy_lag1` déjà décalées par `shift(1)`).
- **Coût de rotation (_turnover_) :** À chaque variation de position $|\text{pos}_t - \text{pos}_{t-1}|$, des frais de **0,10 %** sont déduits du rendement journalier net.
- **Stratégies testées :**
  1. **Trend MA20 (> 0) :** Position `Long (1)` si `r_xlf_ma20 > 0`, sinon `Flat / Cash (0)`.
  2. **Rebond $SPY_{t-1}$ :** Position `Long (1)` si `r_spy_lag1 < -0.005` (baisse de SPY la veille supérieure à 0,5 %), sinon `Flat / Cash (0)`.

---

## 3. Résultats sur Test (2025–2026, Frais 0,10 %)

| Stratégie / Benchmark                             | Rendement Cumulé | Rendement Annualisé | Volatilité Annualisée | Sharpe Ratio | Max Drawdown |
| :------------------------------------------------ | :--------------: | :-----------------: | :-------------------: | :----------: | :----------: |
| **Stratégie : Rebond $SPY_{t-1}$ (frais 0,10 %)** |     +2,86 %      |       +1,55 %       |      **10,60 %**      |    0.1464    | **-9,09 %**  |
| **Stratégie : Trend MA20 (>0, frais 0,10 %)**     |     -0,83 %      |       -0,46 %       |      **10,49 %**      |   -0.0439    |   -14,44 %   |
| **Benchmark : Buy & Hold XLF (frais 0,10 %)**     |     +20,80 %     |      +10,39 %       |        17,33 %        |    0.5998    |   -15,54 %   |
| **Benchmark : Buy & Hold SPY (frais 0,10 %)**     |   **+33,72 %**   |    **+15,99 %**     |        16,68 %        |  **0.9584**  |   -18,76 %   |

---

## 4. Conclusion D05

- La stratégie **Rebond $SPY_{t-1}$** dégage un rendement net positif (`+2,86 %`) tout en réduisant fortement l'exposition au risque : volatilité annualisée ramenée à **10,60 %** et **Max Drawdown limité à `-9,09 %`** (contre `-15,54 %` pour `Buy & Hold XLF` et `-18,76 %` pour `Buy & Hold SPY`).
- Sur la fenêtre `2025–2026` marquée par une tendance haussière globale et des frais de `0,10 %` sur chaque rotation, les benchmarks _Buy & Hold_ conservent un **Sharpe Ratio** supérieur (`0,5998` pour XLF et `0,9584` pour SPY).

---

## 5. Exécution

```bash
python src/backtest.py
```
````
