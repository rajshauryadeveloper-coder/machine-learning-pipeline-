"""Experiment report generator compiling benchmarks & model selections."""

from __future__ import annotations

import datetime
from typing import Any

from src.ml.experiments import run_all_experiments


def generate_markdown_report() -> str:
    """Generate structured Markdown evaluation report for the 5 ML cases."""
    exp = run_all_experiments()
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    c1 = exp["case_1_clv"]
    c2 = exp["case_2_demand"]
    c3 = exp["case_3_order_status"]
    c4 = exp["case_4_churn"]
    c5 = exp["case_5_recommendations"]

    lines = [
        "# Machine Learning Analytics Experiment Report",
        "",
        f"**Generated:** {now_str}",
        "**Framework:** Traditional `scikit-learn` (No Neural Networks)",
        (
            "**Database Schema:** PostgreSQL 5-Table Relational Model "
            "(`categories`, `customers`, `products`, `orders`, `order_items`)"
        ),
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        (
            "This report documents the design, experimentation, and production "
            "selection of machine learning models for 5 distinct eCommerce "
            "business cases. We systematically evaluated linear, tree-based, "
            "distance-based, and **hybrid ensemble architectures** (Voting, "
            "Stacking, and Preprocessing Pipelines) against rigorously computed "
            "metrics (R2, RMSE, Accuracy, F1-Score, ROC-AUC, and Precision@k)."
        ),
        "",
        "| Business Case | Domain Problem | Best Selected Model | Key Metric Performance | Architecture Type |",  # noqa: E501
        "| :--- | :--- | :--- | :--- | :--- |",
        (
            f"| **1. Customer Lifetime Value** | Spend & VIP Tier Prediction | "
            f"{c1['best_regressor']['model_name']} | "
            f"R2 = {c1['best_regressor']['r2_score']}, "
            f"F1 = {c1['best_classifier']['f1_score']} | **Hybrid Ensemble** |"
        ),
        (
            f"| **2. Product Demand** | Velocity & Stock Depletion Risk | "
            f"{c2['best_model']['model_name']} | "
            f"R2 = {c2['best_model']['r2_score']}, "
            f"RMSE = {c2['best_model']['rmse']} | **Gradient Boosting** |"
        ),
        (
            f"| **3. Order Fulfillment Risk** | Delay & Shipping Status Risk | "
            f"{c3['best_model']['model_name']} | "
            f"F1 = {c3['best_model']['f1_score']}, "
            f"ROC-AUC = {c3['best_model']['roc_auc']} | **Hybrid Ensemble** |"
        ),
        (
            f"| **4. Customer Churn** | Inactivity & Churn Risk Tier | "
            f"{c4['best_model']['model_name']} | "
            f"F1 = {c4['best_model']['f1_score']}, "
            f"Accuracy = {c4['best_model']['accuracy']} | **Hybrid Ensemble** |"
        ),
        (
            f"| **5. Product Cross-Sell** | Next-Best Recommendation Ranking | "
            f"{c5['best_model']['model_name']} | "
            f"Precision@3 = {c5['best_model']['precision_at_k']} | "
            f"**Hybrid Collaborative/Content** |"
        ),
        "",
        "---",
        "",
        "## Business Case 1: Customer Lifetime Value (CLV) & VIP Spending Tier",
        "",
        "### Problem Definition",
        (
            "Predict prospective customer spend (Regression) and classify "
            "high-value VIP accounts (Classification) based on historical "
            "basket size, order cadence, and discount utilization."
        ),
        "",
        "#### Regression (Predicting Total Spend in $)",
        "| Model Configuration | R2 Score | RMSE ($) | MAE ($) | 4-Fold CV R2 | Hybrid? |",  # noqa: E501
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for r in c1["regression"]:
        hyb = "✅ Yes" if r["is_hybrid"] else "No"
        lines.append(
            f"| `{r['model_name']}` | `{r['r2_score']}` | `${r['rmse']}` | "
            f"`${r['mae']}` | `{r['cv_mean_r2']} ± {r['cv_std_r2']}` | {hyb} |"
        )

    lines.extend(
        [
            "",
            "#### VIP Classification (Binary: Spend >= $450)",
            "| Model Configuration | Accuracy | F1-Score | Precision | Recall | ROC-AUC | Hybrid? |",  # noqa: E501
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )

    for cl in c1["classification"]:
        hyb = "✅ Yes" if cl["is_hybrid"] else "No"
        lines.append(
            f"| `{cl['model_name']}` | `{cl['accuracy']}` | `{cl['f1_score']}` | "
            f"`${cl['precision']}` | `{cl['recall']}` | `{cl['roc_auc']}` | {hyb} |"
        )

    lines.extend(
        [
            "",
            (
                f"**Best Configuration Rationale:** The **{c1['best_regressor']['model_name']}** "  # noqa: E501
                "achieves the highest generalization score by blending linear "
                "regularization (Ridge) with non-linear tree partitions (Random "
                "Forest and Gradient Boosting)."
            ),
            "",
            "---",
            "",
            "## Business Case 2: Product Demand & Stock Depletion Velocity",
            "",
            "### Problem Definition",
            (
                "Forecast unit sales velocity across product catalog lines to "
                "assess inventory depletion risk (High, Medium, Low) and guide "
                "procurement timing."
            ),
            "",
            "#### Evaluated Configurations",
            "| Model Configuration | R2 Score | RMSE (Units) | MAE (Units) | 3-Fold CV R2 | Hybrid? |",  # noqa: E501
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )

    for m in c2["models"]:
        hyb = "✅ Yes" if m["is_hybrid"] else "No"
        lines.append(
            f"| `{m['model_name']}` | `{m['r2_score']}` | `{m['rmse']}` | "
            f"`{m['mae']}` | `{m['cv_mean_r2']}` | {hyb} |"
        )

    lines.extend(
        [
            "",
            (
                f"**Best Configuration Rationale:** **{c2['best_model']['model_name']}** "  # noqa: E501
                "effectively captures the nonlinear interaction between rating, "
                "unit price, and historical order frequency."
            ),
            "",
            "---",
            "",
            "## Business Case 3: Order Fulfillment Status & Delay Risk",
            "",
            "### Problem Definition",
            (
                "Classify orders at risk of delayed processing or logistics "
                "bottlenecks given payment methods, delivery location, order "
                "value, and item counts."
            ),
            "",
            "#### Evaluated Configurations",
            "| Model Configuration | Accuracy | F1-Score | Precision | Recall | ROC-AUC | Hybrid? |",  # noqa: E501
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )

    for om in c3["models"]:
        hyb = "✅ Yes" if om["is_hybrid"] else "No"
        lines.append(
            f"| `{om['model_name']}` | `{om['accuracy']}` | `{om['f1_score']}` | "
            f"`{om['precision']}` | `{om['recall']}` | `{om['roc_auc']}` | {hyb} |"
        )

    lines.extend(
        [
            "",
            (
                f"**Best Configuration Rationale:** **{c3['best_model']['model_name']}** "  # noqa: E501
                "provides calibrated probability estimates that enable proactive "
                "logistics routing."
            ),
            "",
            "---",
            "",
            "## Business Case 4: Customer Churn Risk & Inactivity Prediction",
            "",
            "### Problem Definition",
            (
                "Predict the likelihood of a customer lapsing into churn based "
                "on recency, purchase cadence, account tenure, and category variety."
            ),
            "",
            "#### Evaluated Configurations",
            "| Model Configuration | Accuracy | F1-Score | Precision | Recall | ROC-AUC | Hybrid? |",  # noqa: E501
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )

    for cm in c4["models"]:
        hyb = "✅ Yes" if cm["is_hybrid"] else "No"
        lines.append(
            f"| `{cm['model_name']}` | `{cm['accuracy']}` | `{cm['f1_score']}` | "
            f"`{cm['precision']}` | `{cm['recall']}` | `{cm['roc_auc']}` | {hyb} |"
        )

    lines.extend(
        [
            "",
            (
                f"**Best Configuration Rationale:** **{c4['best_model']['model_name']}** "  # noqa: E501
                "combines SVM maximum-margin separation with tree-based gradient "
                "boosting to maximize recall on churn risk."
            ),
            "",
            "---",
            "",
            "## Business Case 5: Cross-Sell & Basket Affinity Recommendation",
            "",
            "### Problem Definition",
            (
                "Generate ranked next-best product recommendations for customers "
                "by blending collaborative item co-purchase matrices with "
                "category affinity and item ratings."
            ),
            "",
            "#### Evaluated Configurations",
            "| Model Setup | Precision@3 | Target Top-K | Algorithm Details | Hybrid? |",  # noqa: E501
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
    )

    for rm in c5["models"]:
        hyb = "✅ Yes" if rm["is_hybrid"] else "No"
        lines.append(
            f"| `{rm['model_name']}` | `{rm['precision_at_k']}` | `k={rm['top_k']}` | "
            f"`{rm['algorithm']}` | {hyb} |"
        )

    lines.extend(
        [
            "",
            (
                f"**Best Configuration Rationale:** **{c5['best_model']['model_name']}** "  # noqa: E501
                "solves sparse interaction challenges by augmenting nearest-neighbor "
                "vectors with item quality weighting."
            ),
            "",
            "---",
            "",
            "## Production REST API Endpoints",
            "",
            "All 5 selected models are exposed via REST routes under `/api/v1/ml/`:",
            "- `GET /api/v1/ml/cases`: Metadata for all 5 business cases.",
            "- `GET /api/v1/ml/experiments`: Live benchmark metrics across model runs.",
            "- `GET /api/v1/ml/report`: Markdown and structured report format.",
            "- `POST /api/v1/ml/train`: Triggers re-training across all 5 models.",
            "- `POST /api/v1/ml/predict/clv`: CLV & VIP tier inference.",
            "- `POST /api/v1/ml/predict/demand`: Demand forecasting inference.",
            "- `POST /api/v1/ml/predict/order-status`: Order delay risk inference.",
            "- `POST /api/v1/ml/predict/churn`: Churn probability inference.",
            "- `POST /api/v1/ml/predict/recommend`: Top-K product recommendations.",
        ]
    )

    return "\n".join(lines)


def generate_summary_dict() -> dict[str, Any]:
    """Generate structured summary of all 5 business cases and selected models."""
    exp = run_all_experiments()
    return {
        "total_business_cases": 5,
        "cases": [
            {
                "case_id": "case_1_clv",
                "title": "Customer Lifetime Value & VIP Tier Prediction",
                "type": "Hybrid Regression & Classification",
                "best_regressor": exp["case_1_clv"]["best_regressor"]["model_name"],
                "best_classifier": exp["case_1_clv"]["best_classifier"]["model_name"],
                "r2_score": exp["case_1_clv"]["best_regressor"]["r2_score"],
                "f1_score": exp["case_1_clv"]["best_classifier"]["f1_score"],
            },
            {
                "case_id": "case_2_demand",
                "title": "Product Demand & Inventory Depletion Forecasting",
                "type": "Regression",
                "best_model": exp["case_2_demand"]["best_model"]["model_name"],
                "r2_score": exp["case_2_demand"]["best_model"]["r2_score"],
                "rmse": exp["case_2_demand"]["best_model"]["rmse"],
            },
            {
                "case_id": "case_3_order_status",
                "title": "Order Fulfillment & Delay Risk Prediction",
                "type": "Classification",
                "best_model": exp["case_3_order_status"]["best_model"]["model_name"],
                "f1_score": exp["case_3_order_status"]["best_model"]["f1_score"],
                "roc_auc": exp["case_3_order_status"]["best_model"]["roc_auc"],
            },
            {
                "case_id": "case_4_churn",
                "title": "Customer Churn Risk & Inactivity Prediction",
                "type": "Classification",
                "best_model": exp["case_4_churn"]["best_model"]["model_name"],
                "f1_score": exp["case_4_churn"]["best_model"]["f1_score"],
                "accuracy": exp["case_4_churn"]["best_model"]["accuracy"],
            },
            {
                "case_id": "case_5_recommendations",
                "title": "Cross-Sell & Product Affinity Recommendation",
                "type": "Hybrid Recommendation Ranking",
                "best_model": exp["case_5_recommendations"]["best_model"]["model_name"],
                "precision_at_k": exp["case_5_recommendations"]["best_model"][
                    "precision_at_k"
                ],
            },
        ],
    }
