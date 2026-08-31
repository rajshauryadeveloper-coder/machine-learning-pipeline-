---
type: plan
status: in_review
created: 2026-09-01T00:02:00Z
tags: [machine-learning, scikit-learn, analytics, fastapi, hybrid-models]
---

# Plan: Machine Learning Analytics Pipeline

## Goal
Implement a production-grade Machine Learning Analytics subsystem for the eCommerce platform. Identify 5 core business cases from the PostgreSQL database, conduct experiments across traditional `scikit-learn` algorithms and hybrid ensembles (no neural networks), select the best model configurations, compile an evaluation report, expose REST APIs for real-time inference and experiment inspection, and integrate interactive prediction and analytics panels into the static frontend.

## 5 Business Cases
1. **Customer Lifetime Value (CLV) & VIP Tier Prediction**: Predict total spend ($) and classify high-value VIP customers from purchase history, frequency, and discount metrics.
2. **Product Demand & Stock Depletion Velocity**: Forecast unit sales velocity and classify inventory depletion risk (High/Medium/Low) from price, rating, category, and historical order frequency.
3. **Order Fulfillment Status & Delay Risk Classification**: Predict fulfillment completion vs delay/shipping risk from basket value, item count, payment method, and destination city.
4. **Customer Churn Risk & Inactivity Scoring**: Estimate customer churn probability and risk tier from order recency, purchase cadence, tenure, and category variety.
5. **Cross-Sell & Product Affinity Recommendation**: Score and rank next-best product/category purchase affinity using a hybrid item-affinity and feature-weighted classifier ensemble.

## Scope

### IS IN SCOPE:
- **Feature Engineering & Data Extraction (`src/ml/datasets.py`)**: Extract data from PostgreSQL 5-table schema (`categories`, `customers`, `products`, `orders`, `order_items`) and build feature matrices.
- **Model Experimentation Engine (`src/ml/experiments.py`)**: Train & evaluate traditional `scikit-learn` models (Ridge, Lasso, Random Forest, Gradient Boosting, Logistic Regression, SVC, KNN) and hybrid ensembles (VotingRegressor/Classifier, StackingRegressor/Classifier, Preprocessing Pipelines).
- **Model Inference & Registry (`src/ml/models.py`)**: Train, store, and serve the best performing pipelines with automated training and artifact persistence.
- **ML Experiment Report (`src/ml/report.py` & `.agentflow/worklogs/.../ml_report.md`)**: Benchmark tables, metrics ($R^2$, RMSE, MAE, Accuracy, F1-Score, ROC-AUC), hyperparameter details, and best model rationale.
- **Pydantic Schemas (`src/schemas/ml.py`)**: Schemas for prediction requests/responses, experiment results, and model metadata.
- **FastAPI Endpoints (`src/api/v1/endpoints/ml.py`)**:
  - `GET /api/v1/ml/cases`: 5 business cases & specifications.
  - `GET /api/v1/ml/experiments`: Comprehensive benchmark results across all tested configurations.
  - `GET /api/v1/ml/report`: Markdown & JSON model comparison report.
  - `POST /api/v1/ml/train`: Trigger re-training and re-evaluation.
  - `POST /api/v1/ml/predict/clv`: Predict CLV spend & VIP classification.
  - `POST /api/v1/ml/predict/demand`: Predict product demand & stock depletion risk.
  - `POST /api/v1/ml/predict/order-status`: Predict order delay & fulfillment risk.
  - `POST /api/v1/ml/predict/churn`: Predict customer churn probability.
  - `POST /api/v1/ml/predict/recommend`: Predict product cross-sell recommendations.
- **Frontend Dashboard (`html/index.html`)**:
  - Dedicated "ML Studio & Predictions" tab with interactive inference forms for all 5 business cases.
  - Live Experiment Leaderboard & benchmark comparison metrics.
  - Model retraining trigger and report viewer.
- **Automated Tests (`tests/test_ml_pipeline.py`, `tests/test_ml_api.py`)**: 100% test coverage for feature engineering, model training, hybrid ensembles, and API routes.
- **Documentation (`docs/ml-pipeline.md`, `docs/api.md`)**: Full documentation of business cases, mathematical metrics, and API reference.

### IS NOT IN SCOPE:
- Deep neural networks (PyTorch/TensorFlow).
- External cloud ML deployment (SageMaker/Vertex AI).

## Files Touched

| Path | Change Type | Risk Level | Why |
| --- | --- | --- | --- |
| `pyproject.toml` / `uv.lock` | Modify | Low | Added `scikit-learn`, `pandas`, `numpy`, `joblib`, `scipy` |
| `src/ml/__init__.py` | Add | Low | ML package initialization |
| `src/ml/datasets.py` | Add | Low | Feature engineering & SQL extraction |
| `src/ml/experiments.py` | Add | Medium | Experiment runner & hybrid setups comparison |
| `src/ml/models.py` | Add | Medium | Production inference pipelines & manager |
| `src/ml/report.py` | Add | Low | Report generator & comparison tables |
| `src/schemas/ml.py` | Add | Low | Pydantic validation schemas for ML |
| `src/api/v1/endpoints/ml.py` | Add | Medium | REST API routes for ML inference & experiments |
| `src/api/v1/router.py` | Modify | Low | Register ML router |
| `src/main.py` | Modify | Low | Initialize ML models on startup |
| `html/index.html` | Modify | Medium | Add ML Studio UI, interactive prediction forms & leaderboard |
| `tests/test_ml_pipeline.py` | Add | Medium | Unit & integration tests for ML models |
| `tests/test_ml_api.py` | Add | Medium | API route tests for ML endpoints |
| `docs/ml-pipeline.md` | Add | Low | Architecture & model report docs |
| `docs/api.md` | Modify | Low | Update API documentation with ML endpoints |

## Dependencies Added
- `scikit-learn>=1.9.0`
- `pandas>=3.0.5`
- `numpy>=2.4.6`
- `joblib>=1.6.0`
- `scipy>=1.17.1`

## Definition of Done
- [ ] 5 ML business cases clearly identified, documented, and implemented.
- [ ] Multiple `scikit-learn` standalone and hybrid configurations evaluated for each case.
- [ ] Best model configurations selected and documented with evaluation metrics ($R^2$, RMSE, Accuracy, F1, ROC-AUC).
- [ ] REST API endpoints for all 5 business cases and experiment report implemented.
- [ ] Frontend UI provides interactive forms for predictions and displays experiment benchmarks.
- [ ] Verification suite (`./scripts/flow verify`) passes with 0 failures, clean flake8/black, and >=60% test coverage.
- [ ] Documentation updated in `docs/`.
