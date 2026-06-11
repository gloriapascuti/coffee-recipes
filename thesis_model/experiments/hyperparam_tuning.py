from itertools import product

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


LR_GRID = {
    "C": [0.1, 1.0, 10.0],
}

RF_GRID = {
    "n_estimators":     [200, 400],
    "max_depth":        [10, 14, 20],
    "min_samples_leaf": [1, 2, 4],
}

GB_GRID = {
    "n_estimators":  [200, 350],
    "learning_rate": [0.03, 0.05, 0.1],
    "max_depth":     [3, 4, 5],
}


def _grid_search(estimator_cls, param_grid, fixed_params,
                 X_train, y_train, X_val, y_val):
    keys = list(param_grid.keys())
    combinations = list(product(*param_grid.values()))

    results = []
    best_auc = -np.inf
    best_params = None

    print(f"\n  Grid search for {estimator_cls.__name__} "
          f"({len(combinations)} combinations)")
    for combo in combinations:
        params = dict(zip(keys, combo))
        model = estimator_cls(**fixed_params, **params)
        model.fit(X_train, y_train)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, y_pred_proba)

        is_best = auc > best_auc
        marker = "*" if is_best else " "
        print(f"    {marker} {params}  ->  val ROC-AUC = {auc:.4f}")

        results.append({**params, "val_roc_auc": auc})
        if is_best:
            best_auc = auc
            best_params = params

    print(f"  Best for {estimator_cls.__name__}: "
          f"val ROC-AUC = {best_auc:.4f}, params = {best_params}")
    return best_params, results


def grid_search_lr(X_train, y_train, X_val, y_val):
    fixed = dict(
        random_state=42, class_weight="balanced",
        max_iter=3000, solver="lbfgs",
    )
    return _grid_search(LogisticRegression, LR_GRID, fixed,
                        X_train, y_train, X_val, y_val)


def grid_search_rf(X_train, y_train, X_val, y_val):
    fixed = dict(
        random_state=42, n_jobs=-1, class_weight="balanced",
        min_samples_split=4,
    )
    return _grid_search(RandomForestClassifier, RF_GRID, fixed,
                        X_train, y_train, X_val, y_val)


def grid_search_gb(X_train, y_train, X_val, y_val):
    fixed = dict(random_state=42)
    return _grid_search(GradientBoostingClassifier, GB_GRID, fixed,
                        X_train, y_train, X_val, y_val)
