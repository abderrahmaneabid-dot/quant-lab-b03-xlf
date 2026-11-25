# Livrable D04 — Modélisation de la Volatilité & du Risque (Variante B03 : XLF)

**Actif modélisé :** `XLF` (_Financial Select Sector SPDR Fund_)  
**Script :** `src/models/volatility_models.py`  
**Rapport généré :** `reports/d04_risk_summary.csv`

---

## 1. Objectif du Livrable D04

Suite à la mise en évidence d'un fort _volatility clustering_ dans les résidus des modèles de moyenne (`Ljung-Box p = 0.0000` en D03), ce livrable modélise la **volatilité conditionnelle** de `XLF` via un modèle **GARCH(1,1)** afin d'estimer le risque extrême (**Value at Risk à 99 %** et **Expected Shortfall à 99 %**).

---

## 2. Protocole Méthodologique (Sans Look-Ahead Bias)

- **Calibration (`Train` : 2018–2022) :** Estimation du modèle `GARCH(1,1)` (distribution normale, moyenne constante $\mu$) uniquement sur l'échantillon d'entraînement ($\hat{\mu} = 0{,}0676\,\%$, $p = 0{,}0348$).
- **Prévision hors échantillon (`Validation` : 2023–2024) :** Projection de la volatilité conditionnelle $\hat{\sigma}_t$ sur la période de validation en fixant les paramètres estimés sur `Train` (`fix(res.params)`), sans ré-estimation ni fuite d'information future.
- **Indicateurs de risque (`alpha = 1 %`) :**
  - **VaR 99 % :** Perte journalière maximale attendue au seuil de confiance de 99 %.
  - **Expected Shortfall (ES 99 %) :** Perte moyenne conditionnelle lorsque la perte dépasse la VaR 99 %.
- **Benchmark de comparaison :** Volatilité historique glissante sur 20 jours décalée d'une séance (`Rolling Vol 20j` avec `shift(1)`).

---

## 3. Résultats sur Validation (2023–2024)

| Modèle de Risque                | Volatilité Moyenne Val | VaR 99 % Moyenne (perte) | ES 99 % Moyenne (perte) | Exceptions VaR 99 % (%) | Cible Théorique (%) |
| :------------------------------ | :--------------------: | :----------------------: | :---------------------: | :---------------------: | :-----------------: |
| **GARCH(1,1) Normal**           |        0.010647        |    0.024091 (2,41 %)     |    0.027699 (2,77 %)    |      **0.5976 %**       |      1.0000 %       |
| **Benchmark : Rolling Vol 20j** |        0.008982        |    0.020895 (2,09 %)     |    0.023938 (2,39 %)    |        2.7888 %         |      1.0000 %       |

---

## 4. Conclusion D04

- Le modèle **GARCH(1,1)** affiche un taux de dépassement empirique de **0,60 %**, proche et inférieur au seuil théorique de **1,00 %**, traduisant une estimation prudente et réactive du risque de queue.
- À l'inverse, la **Rolling Vol 20j** sous-estime le risque en période de validation avec **2,79 % d'exceptions** (près de 3 fois la cible théorique).

---

## 5. Exécution

```bash
python src/models/volatility_models.py
```
