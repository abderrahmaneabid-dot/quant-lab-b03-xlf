## Partie II — Économétrie de la Moyenne : ARIMA vs SARIMAX (Livrable D03)

### 1. Fichiers & Livrables Produits

- `src/models/mean_models.py` : Script automatisé exécutant les tests de stationnarité, les 4 baselines, la sélection d'ordre par AIC et l'évaluation hors échantillon.
- `notebooks/02_model_lab.ipynb` : Notebook d'analyse exploratoire et de diagnostic graphique (stationnarité, ACF/PACF, résidus, comparaison RMSE).
- `reports/d03_model_comparison.csv` & `reports/figures/` : Export des métriques et des graphiques de diagnostic.

### 2. Validation de la Stationnarité (Période Train : 2018–2022)

La confrontation des tests **ADF** ($H_0$ : non-stationnaire) et **KPSS** ($H_0$ : stationnaire) valide le passage aux rendements logarithmiques :

| Série analysée     | Stat. ADF | p-value ADF | Stat. KPSS | p-value KPSS | Verdict                 |
| :----------------- | :-------: | :---------: | :--------: | :----------: | :---------------------- |
| **Prix brut XLF**  |  -1.3591  |   0.6017    |   3.9268   |    0.0100    | Non-stationnaire $I(1)$ |
| **Log Return XLF** | -10.5756  |   0.0000    |   0.0793   |    0.1000    | **Stationnaire $I(0)$** |

### 3. Comparaison Hors Échantillon (Validation : 2023–2024)

Après calibration sur `Train` par minimisation du critère **AIC**, les modèles `ARIMA(2,0,2)` et `SARIMAX(2,0,2)` ont été évalués sur `Validation` (`refit=False`) face à 4 modèles naïfs de référence :

| Modèle                                      |    Ordre    |     AIC      |     BIC      |  RMSE (Val)  |  MAE (Val)   | Ljung-Box $p$ (lag 10 / 20) |
| :------------------------------------------ | :---------: | :----------: | :----------: | :----------: | :----------: | :-------------------------: |
| **Baseline : Naïf Zéro ($\hat{r}_t = 0$)**  |      -      |      -       |      -       | **0.009594** | **0.007109** |              -              |
| **ARIMA (XLF seul)**                        | `(2, 0, 2)` | **-6585.38** | **-6554.66** |   0.009679   |   0.007206   |       0.0000 / 0.0000       |
| **SARIMAX (XLF + $SPY_{t-1}$)**             | `(2, 0, 2)` |   -6583.07   |   -6547.24   |   0.009687   |   0.007213   |       0.0000 / 0.0000       |
| **Baseline : Moyenne Mobile 20j**           |      -      |      -       |      -       |   0.009793   |   0.007248   |              -              |
| **Baseline : Moyenne Mobile 5j**            |      -      |      -       |      -       |   0.010469   |   0.007836   |              -              |
| **Baseline : Naïf Persistance ($r_{t-1}$)** |      -      |      -       |      -       |   0.013299   |   0.009725   |              -              |

### 4. Conclusions Scientifiques & Transition vers la Volatilité (D04)

- **Réponse à la question B03 :** L'ajout de la variable exogène retardée $SPY_{t-1}$ n'améliore pas la prévision linéaire de la moyenne. Son coefficient (`-0.035148`) est statistiquement non significatif (`p-value = 0.428451 > 0.05`) et les critères AIC/BIC pénalisent cette complexité supplémentaire. Ce résultat est cohérent avec l'**Hypothèse d'Efficience des Marchés (EMH)** sur deux ETFs américains très liquides.
- **Diagnostic des résidus :** Le rejet de l'hypothèse de bruit blanc au test de **Ljung-Box** ($p = 0{,}0000$) ainsi que l'autocorrélation marquée des résidus au carré révèlent un fort phénomène de **clustering de volatilité** (notamment lors du choc COVID-19 de 2020), justifiant le passage à une modélisation de la variance conditionnelle (**GARCH(1,1)**) dans la suite du projet.
