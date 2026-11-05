"""SHAP explanations for the tree models (owner: Ayo; Y11).

Works for Random Forest and XGBoost (src/models_supervised.py) and for Arva's Isolation Forest
(src/models_unsupervised.py). Usage, e.g. for Arva's case studies (A19):

    from src.explain import explain_sample, get_shap_values, plot_summary, plot_waterfall, top_features
    from src.features import get_model_matrix
    from src.models_supervised import train_and_score_supervised

    scores, info = train_and_score_supervised(df, "xgboost", save=False)
    rows = explain_sample(df)                        # all test positives + 5,000 test negatives
    X, _, names = get_model_matrix(rows)
    sv = get_shap_values(info["pipeline"], X)        # or info["detector"] from train_and_score()
    top_features(sv, names)                          # mean |SHAP| ranking
    plot_summary(sv, X, name="shap_summary_xgboost") # beeswarm -> results/figures/
    plot_waterfall(sv, X, row=0, name="shap_waterfall_example")

Sign convention: a positive SHAP value always pushes a user-day towards "malicious / anomalous".
For RF the values are for class 1 (probability), for XGBoost they are in log-odds, and for
Isolation Forest they explain the anomaly score (-decision_function), so the sign of shap's raw
path-length values is flipped.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import IsolationForest

from src.config import FIGURES_DIR, RANDOM_STATE

N_NEGATIVES = 5000


def explain_sample(df: pd.DataFrame, split="test", n_negatives=N_NEGATIVES, seed=RANDOM_STATE):
    """Rows to explain (Y11 step 2): every malicious row of `split` + up to n_negatives random
    normal rows of it, in their original order."""
    rows = df[df["split"] == split]
    neg = rows[rows["label"] == 0]
    neg = neg.sample(min(n_negatives, len(neg)), random_state=seed)
    return rows.loc[rows.index.isin(neg.index) | (rows["label"] == 1)]


def _model_and_inputs(fitted, X: pd.DataFrame):
    """The final estimator and X passed through the pipeline's transform steps (the scaler).
    Accepts a sklearn/imblearn Pipeline or an object holding one in `.pipeline` (Arva's
    IsolationForestDetector). Resamplers such as SMOTE have no transform and are skipped."""
    pipeline = getattr(fitted, "pipeline", fitted)
    steps = getattr(pipeline, "steps", None)
    if steps is None:
        return pipeline, X
    Xt = X
    for _, step in steps[:-1]:
        if hasattr(step, "transform"):
            Xt = step.transform(Xt)
    return steps[-1][1], pd.DataFrame(np.asarray(Xt), index=X.index, columns=X.columns)


def get_shap_values(fitted_pipeline, X: pd.DataFrame) -> shap.Explanation:
    """SHAP values of every row of X (Y11 step 1), one column per feature.

    The model is taken out of the pipeline and X is scaled the same way before TreeExplainer runs.
    The returned Explanation keeps X's unscaled values in `.data` (what the plots show) and the
    feature names. For RF classifiers the class-1 values are kept.
    """
    model, Xs = _model_and_inputs(fitted_pipeline, X)
    explanation = shap.TreeExplainer(model)(Xs, check_additivity=False)
    values, base = np.asarray(explanation.values), np.asarray(explanation.base_values)
    if values.ndim == 3:                       # (rows, features, classes): keep class 1
        values, base = values[..., 1], base[..., 1]
    if isinstance(model, IsolationForest):     # path length: higher = more normal -> flip
        values, base = -values, -base
    return shap.Explanation(values=values, base_values=base, data=X.to_numpy(),
                            feature_names=list(X.columns))


def top_features(shap_values: shap.Explanation, feature_names=None, k=10) -> pd.DataFrame:
    """Mean |SHAP| per feature, largest first (Y11 step 5)."""
    names = feature_names if feature_names is not None else shap_values.feature_names
    importance = np.abs(np.asarray(shap_values.values)).mean(axis=0)
    table = pd.DataFrame({"feature": names, "mean_abs_shap": importance})
    table = table.sort_values("mean_abs_shap", ascending=False).head(k).reset_index(drop=True)
    table.insert(0, "rank", np.arange(1, len(table) + 1))
    return table


def _save(fig, name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES_DIR / f"{name}.{ext}", dpi=300, bbox_inches="tight")


def plot_summary(shap_values: shap.Explanation, X=None, name="shap_summary", max_display=15):
    """Beeswarm plot of global importance (Y11 step 3), saved as PNG and PDF."""
    if X is not None:
        shap_values = shap.Explanation(shap_values.values, shap_values.base_values,
                                       data=np.asarray(X), feature_names=list(X.columns))
    plt.figure()
    shap.plots.beeswarm(shap_values, max_display=max_display, show=False)
    fig = plt.gcf()
    _save(fig, name)
    plt.close(fig)
    return fig


def plot_waterfall(shap_values: shap.Explanation, X, row, name="shap_waterfall", max_display=10):
    """Explanation of one user-day (Y11 step 4). `row` is a position (int) or an index label of X."""
    pos = X.index.get_loc(row) if (X is not None and row in X.index and not isinstance(row, int)) \
        else int(row)
    plt.figure()
    shap.plots.waterfall(shap_values[pos], max_display=max_display, show=False)
    fig = plt.gcf()
    _save(fig, name)
    plt.close(fig)
    return fig


def demo(features="features_v0"):
    """Y11 "done when": every function on the v0 XGBoost and Isolation Forest."""
    from src.config import PROCESSED_DIR
    from src.features import get_model_matrix
    from src.models_supervised import train_and_score_supervised
    from src.models_unsupervised import train_and_score

    df = pd.read_parquet(PROCESSED_DIR / f"{features}.parquet")
    rows = explain_sample(df)
    X, _, names = get_model_matrix(rows)
    version = features.replace("features_", "")
    fitted = {"xgboost": train_and_score_supervised(df, "xgboost", save=False)[1]["pipeline"],
              "iforest": train_and_score(df, "iforest", save=False)[1]["detector"]}
    print(f"explaining {len(X):,} {features} test rows ({int(rows['label'].sum())} malicious)")
    for model, fit in fitted.items():
        sv = get_shap_values(fit, X)
        plot_summary(sv, X, name=f"shap_summary_{model}_{version}")
        worst = int(np.argmax(sv.values.sum(axis=1)))
        plot_waterfall(sv, X, worst, name=f"shap_waterfall_{model}_{version}")
        print(f"\n{model}: top features by mean |SHAP| "
              f"(figures shap_summary_{model}_{version}, shap_waterfall_{model}_{version})")
        print(top_features(sv, names, k=len(names)).to_string(index=False))


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["demo"]:
        demo(*sys.argv[2:3])
    else:
        print(__doc__)
