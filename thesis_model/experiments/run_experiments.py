import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
THESIS_MODEL_DIR = THIS_DIR.parent

if str(THESIS_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(THESIS_MODEL_DIR))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler

from trained_model import (
    load_and_preprocess_data,
    split_data_3way,
    train_all_models,
    select_threshold_on_validation,
    final_test_evaluation,
    _evaluate_on,
)

from experiments.postprocessing_study import (
    run_postprocessing_study,
    run_learned_postprocessing_study,
)
from experiments.hyperparam_tuning import (
    grid_search_gb,
    grid_search_lr,
    grid_search_rf,
)
from experiments.postprocessing import PlattCalibrator


OUT_DIR = THIS_DIR / "outputs"
DATA_CSV = THESIS_MODEL_DIR / "data" / "nhanes_cvd_training_data.csv"


def plot_confusion_matrix(cm, title, out_path):
    fig, ax = plt.subplots(figsize=(5.0, 4.0))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Predicted alive", "Predicted CVD death"])
    ax.set_yticklabels(["Actual alive", "Actual CVD death"])
    ax.set_title(title, fontsize=11)
    total = cm.sum()
    threshold = cm.max() / 2
    for i in range(2):
        for j in range(2):
            pct = (cm[i, j] / total * 100) if total else 0.0
            ax.text(j, i, f"{cm[i, j]:,}\n({pct:.1f}%)",
                    ha="center", va="center", fontsize=13,
                    color="white" if cm[i, j] > threshold else "black")
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_caffeine_dose_response(out_path):
    daily = np.linspace(0, 800, 400)

    rr = np.where(
        daily <= 300,
        1.0 - 0.08 * (daily / 300),
        np.where(
            daily <= 400,
            0.92 + 0.08 * (daily - 300) / 100,
            np.where(
                daily <= 600,
                1.0 + 0.08 * (daily - 400) / 200,
                1.08 + 0.15 * (daily - 600) / 200,
            ),
        ),
    )

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(daily, rr, color="#1f4f87", linewidth=2.5)
    ax.axhline(1.0, color="grey", linestyle="--", linewidth=0.8)

    ax.axvspan(0,   300, alpha=0.10, color="#2ca02c", label="Neutral / protective (0-300 mg)")
    ax.axvspan(300, 400, alpha=0.10, color="#ffbf00", label="Mild (300-400 mg)")
    ax.axvspan(400, 600, alpha=0.10, color="#ff7f0e", label="Elevated (400-600 mg)")
    ax.axvspan(600, 800, alpha=0.10, color="#d62728", label="High (> 600 mg)")

    ax.set_xlabel("Daily caffeine intake (mg)", fontsize=11)
    ax.set_ylabel("Relative cardiovascular risk", fontsize=11)
    ax.set_xlim(0, 800)
    ax.set_ylim(0.85, 1.30)
    ax.set_title("U-shaped caffeine dose-response curve (schematic; based on "
                 "Larsson 2014)", fontsize=11)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def slugify(name):
    return (
        name.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("+", "and")
    )


def main():
    OUT_DIR.mkdir(exist_ok=True)
    print("=" * 70)
    print("THESIS EXPERIMENTS")
    print(f"Outputs: {OUT_DIR}")
    print("=" * 70)

    print("\n[1/12] Loading and splitting data")
    print("-" * 70)
    X, y, feature_names, encoders = load_and_preprocess_data(DATA_CSV)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data_3way(X, y, random_state=42)

    print("[2/12] Standardising features (train statistics applied to val/test)")
    print("-" * 70)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s   = scaler.transform(X_val)
    X_test_s  = scaler.transform(X_test)

    print("\n[3/12] Grid search for hyperparameters on the validation set")
    print("=" * 70)
    lr_best, lr_results = grid_search_lr(X_train_s, y_train, X_val_s, y_val)
    rf_best, rf_results = grid_search_rf(X_train_s, y_train, X_val_s, y_val)
    gb_best, gb_results = grid_search_gb(X_train_s, y_train, X_val_s, y_val)

    tuning_df = pd.concat(
        [
            pd.DataFrame([{"model": "Logistic Regression", **r} for r in lr_results]),
            pd.DataFrame([{"model": "Random Forest",       **r} for r in rf_results]),
            pd.DataFrame([{"model": "Gradient Boosting",   **r} for r in gb_results]),
        ],
        ignore_index=True,
    )
    tuning_df.to_csv(OUT_DIR / "hyperparameter_tuning.csv", index=False)
    print(f"\n  -> saved hyperparameter_tuning.csv  ({len(tuning_df)} rows)")

    print("\n[4/12] Training final models with best hyperparameters")
    print("=" * 70)
    results = train_all_models(X_train_s, y_train, X_val_s, y_val)

    print("\n[5/14] Confusion matrices on the TEST set (tau = 0.5)")
    print("=" * 70)
    cm_rows = []
    for name, r in results.items():
        m = _evaluate_on(r["model"], X_test_s, y_test, threshold=0.5)
        cm = confusion_matrix(y_test, m["y_pred"])
        plot_confusion_matrix(
            cm, f"{name}  (test set, tau = 0.5)",
            OUT_DIR / f"cm_{slugify(name)}.png",
        )
        cm_rows.append({
            "model": name,
            "tn": int(cm[0, 0]), "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]), "tp": int(cm[1, 1]),
        })
        print(f"  {name:<22} TN={cm[0,0]:>5,}  FP={cm[0,1]:>5,}  "
              f"FN={cm[1,0]:>5,}  TP={cm[1,1]:>5,}")
    pd.DataFrame(cm_rows).to_csv(OUT_DIR / "confusion_matrices_test.csv", index=False)

    print("\n[6/14] Model comparison table on the TEST set (tau = 0.5)")
    print("=" * 70)
    comp_rows = []
    for name, r in results.items():
        m = _evaluate_on(r["model"], X_test_s, y_test, threshold=0.5)
        comp_rows.append({
            "model": name,
            "accuracy":  m["accuracy"],
            "precision": m["precision"],
            "recall":    m["recall"],
            "f1":        m["f1"],
            "roc_auc":   m["roc_auc"],
            "mcc":       m["mcc"],
        })
    comp_df = pd.DataFrame(comp_rows)
    comp_df.to_csv(OUT_DIR / "model_comparison_test.csv", index=False)
    print(comp_df.to_string(index=False, float_format="{:.3f}".format))

    print("\n[7/14] Per-model threshold sweep on the VALIDATION set")
    print("=" * 70)
    print("  Selecting tau per model by maximising F1 (MCC as tie-breaker).\n")

    per_model_thresholds = {}
    sweep_rows = []
    for name, r in results.items():
        print(f"\n  --- {name} ---")
        tau_opt, sweep = select_threshold_on_validation(
            r["model"], X_val_s, y_val,
        )
        per_model_thresholds[name] = float(tau_opt)
        for row in sweep:
            sweep_rows.append({"model": name, **row})

    pd.DataFrame(sweep_rows).to_csv(
        OUT_DIR / "threshold_sweep_validation_all_models.csv", index=False,
    )
    print("\n  Optimal thresholds (chosen on validation):")
    for name, tau in per_model_thresholds.items():
        print(f"    {name:<22} tau* = {tau:.2f}")

    print("\n[8/14] Fair comparison on the TEST set "
          "(each model at its own tau*)")
    print("=" * 70)
    fair_rows = []
    for name, r in results.items():
        tau = per_model_thresholds[name]
        m = _evaluate_on(r["model"], X_test_s, y_test, threshold=tau)
        fair_rows.append({
            "model": name,
            "tau_opt":   tau,
            "accuracy":  m["accuracy"],
            "precision": m["precision"],
            "recall":    m["recall"],
            "f1":        m["f1"],
            "roc_auc":   m["roc_auc"],
            "mcc":       m["mcc"],
        })
    fair_df = pd.DataFrame(fair_rows)
    fair_df.to_csv(OUT_DIR / "model_comparison_test_fair.csv", index=False)
    print(fair_df.to_string(index=False, float_format="{:.3f}".format))

    print("\n  Ranking on primary metrics (higher = better):")
    for metric in ("roc_auc", "f1", "mcc", "recall"):
        winner = fair_df.sort_values(metric, ascending=False).iloc[0]
        print(f"    {metric.upper():<10} -> {winner['model']:<22} "
              f"({metric} = {winner[metric]:.3f}, tau = {winner['tau_opt']:.2f})")

    print("\n[9/14] Confusion matrices on TEST at each model's optimal tau")
    print("=" * 70)
    fair_cm_rows = []
    for name, r in results.items():
        tau = per_model_thresholds[name]
        m = _evaluate_on(r["model"], X_test_s, y_test, threshold=tau)
        cm = confusion_matrix(y_test, m["y_pred"])
        plot_confusion_matrix(
            cm, f"{name}  (test set, tau* = {tau:.2f})",
            OUT_DIR / f"cm_{slugify(name)}_optimal_tau.png",
        )
        fair_cm_rows.append({
            "model": name,
            "tau_opt": tau,
            "tn": int(cm[0, 0]), "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]), "tp": int(cm[1, 1]),
        })
        print(f"  {name:<22} tau*={tau:.2f}  "
              f"TN={cm[0,0]:>5,}  FP={cm[0,1]:>5,}  "
              f"FN={cm[1,0]:>5,}  TP={cm[1,1]:>5,}")
    pd.DataFrame(fair_cm_rows).to_csv(
        OUT_DIR / "confusion_matrices_test_optimal_tau.csv", index=False,
    )

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    print(f"\n[10/14] Best model by validation ROC-AUC: {best_name}")
    print("=" * 70)

    chosen = results[best_name]
    optimal_tau = per_model_thresholds[best_name]
    pd.DataFrame(
        [row for row in sweep_rows if row["model"] == best_name]
    ).drop(columns=["model"]).to_csv(
        OUT_DIR / "threshold_sweep_validation.csv", index=False,
    )

    print("\n[11/14] Fitting Platt calibration on the validation set")
    print("=" * 70)
    p_val_raw = chosen["model"].predict_proba(X_val_s)[:, 1]
    platt = PlattCalibrator().fit(p_val_raw, y_val)
    print(f"  Platt parameters: {platt.params}")

    print("\n[12/14] Final test-set evaluation")
    print("=" * 70)
    final_metrics, final_cm = final_test_evaluation(
        chosen["model"], optimal_tau, X_test_s, y_test,
        model_name=best_name,
    )

    print("\n[13/14] Post-processing impact study on the test set")
    print("=" * 70)

    print("\n  13a. Legacy formula (hand-tuned constants 0.01 / 0.02)")
    study_df = run_postprocessing_study(
        chosen["model"], optimal_tau,
        X_test_scaled=X_test_s, y_test=y_test,
        X_test_raw=X_test, feature_names=feature_names,
        platt_calibrator=platt,
        clinical_weight=0.01,
        caffeine_weight=0.01,
        caffeine_period_days=365,
    )
    study_df.to_csv(OUT_DIR / "postprocessing_study_results.csv", index=False)

    print("\n  13b. Learned coefficients (replaces magic numbers)")
    study_learned_df, study_coefs_df = run_learned_postprocessing_study(
        chosen["model"],
        X_val_scaled=X_val_s, y_val=y_val, X_val_raw=X_val,
        X_test_scaled=X_test_s, y_test=y_test, X_test_raw=X_test,
        feature_names=feature_names,
        caffeine_period_days=365,
    )
    study_learned_df.to_csv(
        OUT_DIR / "postprocessing_study_results_learned.csv", index=False,
    )
    study_coefs_df.to_csv(
        OUT_DIR / "learned_pp_coefficients.csv", index=False,
    )

    print("\n[14/14] Generating Chapter-3 figure")
    print("=" * 70)
    fig_path = OUT_DIR / "caffeine_dose_response_curve.png"
    plot_caffeine_dose_response(fig_path)
    print(f"  -> {fig_path}")

    summary = {
        "split": {
            "train": int(len(y_train)),
            "val":   int(len(y_val)),
            "test":  int(len(y_test)),
        },
        "best_hyperparameters": {
            "Logistic Regression": lr_best,
            "Random Forest":       rf_best,
            "Gradient Boosting":   gb_best,
        },
        "per_model_optimal_thresholds": per_model_thresholds,
        "fair_comparison_test": {
            row["model"]: {
                "tau_opt":   float(row["tau_opt"]),
                "accuracy":  float(row["accuracy"]),
                "precision": float(row["precision"]),
                "recall":    float(row["recall"]),
                "f1":        float(row["f1"]),
                "roc_auc":   float(row["roc_auc"]),
                "mcc":       float(row["mcc"]),
            }
            for row in fair_rows
        },
        "selection_criterion": "max validation ROC-AUC (Fawcett 2006), "
                               "ensemble tie-breaker at <=0.001",
        "best_model": best_name,
        "optimal_threshold": float(optimal_tau),
        "platt_parameters": platt.params,
        "final_test_metrics": {
            k: (float(v) if not isinstance(v, np.ndarray) else None)
            for k, v in final_metrics.items()
            if k not in ("y_pred", "y_pred_proba")
        },
        "learned_pp_study": [
            {
                "condition": row["condition"],
                "tau_opt":   float(row["tau_opt"]),
                "f1":        float(row["f1"]),
                "recall":    float(row["recall"]),
                "precision": float(row["precision"]),
                "mcc":       float(row["mcc"]),
                "roc_auc":   float(row["roc_auc"]),
            }
            for _, row in study_learned_df.iterrows()
        ],
        "learned_pp_coefficients": {
            cond: {
                name: {
                    "beta":    float(g.loc[g["name"] == name, "beta"].iloc[0]),
                    "se":      float(g.loc[g["name"] == name, "se"].iloc[0]),
                    "p_value": (
                        float(g.loc[g["name"] == name, "p_value"].iloc[0])
                        if not pd.isna(g.loc[g["name"] == name, "p_value"].iloc[0])
                        else None
                    ),
                }
                for name in g["name"].unique()
            }
            for cond, g in study_coefs_df.groupby("condition", sort=False)
        },
    }
    with open(OUT_DIR / "experiment_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 70)
    print("EXPERIMENTS COMPLETE")
    print("=" * 70)
    print(f"Outputs in: {OUT_DIR}")
    for p in sorted(OUT_DIR.iterdir()):
        if p.is_file():
            size = p.stat().st_size
            print(f"  {p.name:<45}  {size:>8,} bytes")


if __name__ == "__main__":
    main()
