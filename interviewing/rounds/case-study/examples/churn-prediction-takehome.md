# Worked Example: Churn Prediction Take-Home

**Format:** Take-home, 3-hour timebox
**Prompt:** "Here's 100K rows of churn data — what do you do in 3 hours?"
**Template:** Full 8-section walkthrough, adapted for take-home format

---

## How to read this example

This is a simulated take-home submission — both the analytical notebook and the memo writeup. The memo is the primary deliverable; the notebook backs it up. In the 3-hour timebox, 40 minutes go to the memo.

The key discipline: state assumptions first, be honest about data issues, close with "next steps / not done."

---

## Assumptions (first paragraph — always)

> "I assumed this is a B2C subscription product (monthly billing). I treated churn as binary: did the customer cancel within 30 days of this observation date? I assumed the `churned` column is the label and that it was generated from actual cancellations, not inferred. I assumed no data after the observation date is available at prediction time — I will check for leakage. I assumed the goal is to identify customers to target with a retention intervention (email campaign or offer), so precision on the top decile matters more than overall recall."

---

## Section 1: Objective

**Business objective:** Reduce monthly churn rate from 8% to 3.8% over 90 days, representing $1.2M/year in retained revenue (at $200 average LTV per customer).

**ML objective:** Build a churn classifier with AUROC ≥ 0.82 on a held-out test set, with a top-decile precision ≥ 65% (we want 65% of the customers we contact to actually be at risk of churning).

**Why AUROC over accuracy:** The dataset is 8% positive rate — a model that predicts "never churns" gets 92% accuracy and is useless. AUROC measures discrimination ability independent of threshold, which is what we need before the business tells us its campaign budget.

---

## Section 2: Constraints

| Constraint | Note |
|-----------|------|
| Timebox | 3 hours. No extended analysis. |
| Inference time | Batch scoring — can tolerate minutes, not milliseconds. |
| Interpretability | Retention team needs to understand why a customer is at risk (for message personalization). SHAP on top features is a requirement, not an afterthought. |
| Data | One flat CSV. No feature store, no external enrichment available in this timebox. |

---

## Section 3: Data sources & EDA

**Data audit (30 minutes):**

Dataset: 100K rows, 28 columns. Key findings:

| Finding | Action taken |
|---------|-------------|
| `last_contact_date` is post-observation-date for 12% of rows | Drop column — leakage. This date reflects when the churn intervention happened, not a prediction feature. |
| `monthly_spend` has 4.2% missing values | Impute with median by `plan_tier` (not global median — spend varies significantly by tier). |
| `signup_date` — raw date column | Engineer: `tenure_days = observation_date - signup_date`. Drop raw date. |
| `support_contacts_last_90d` — right-skewed | Log-transform. |
| `product_category` — 47 unique values | Group to top-10 + "other". Label encode. |
| Class imbalance | 8% positive rate. Use `scale_pos_weight` in LightGBM. Do not oversample — it tends to hurt calibration on this kind of dataset. |

**Leakage check — the first thing I do every time:**
Any feature that couldn't have been known at prediction time is leakage. Red flags to check: any event that happens after churn (e.g., "account_closed_date"), any feature derived from the churn event itself. Found one (`last_contact_date`) — dropped.

---

## Section 4: Baseline first

**Baseline model: logistic regression on 5 features**

Features: `tenure_days`, `monthly_spend`, `support_contacts_last_90d`, `logins_last_30d`, `plan_tier_encoded`.

Baseline AUROC on validation set: **0.71**

This is our anchor. Any model we build must beat 0.71 to justify the complexity. It also tells us the signal is real — 0.71 is well above chance (0.50).

---

## Section 5: MVP pipeline

**Model: LightGBM**

**Why LightGBM over alternatives:**
- 100K rows with ~25 features — this is the tabular sweet spot for gradient boosting. Neural nets typically need millions of rows to justify their parameter overhead on this kind of structured data.
- Handles mixed feature types (categorical + numeric) natively.
- `scale_pos_weight` built-in for class imbalance.
- Fast training (under 2 minutes for this dataset) — crucial in a 3-hour timebox.
- SHAP integration for feature importance.

**Pipeline:**
```python
# 1. Train/val/test split: 70/15/15, stratified on churn label
# 2. Feature preprocessing:
#    - Numeric: median imputation by plan_tier, log-transform skewed
#    - Categorical: label encoding (LightGBM handles natively)
# 3. LightGBM with 5-fold CV on train set
#    - Key hyperparams tuned: max_depth (5–8), num_leaves (31–63),
#      learning_rate (0.05–0.1), scale_pos_weight (11.5 = 92/8)
# 4. Best params applied to full train set → eval on held-out test set
# 5. SHAP values computed on test set for top-5 feature importance
```

**Results:**
| Metric | Baseline (LR) | LightGBM |
|--------|--------------|----------|
| AUROC | 0.71 | 0.83 |
| Top-decile precision | 41% | 68% |
| Top-decile recall | 22% | 36% |

AUROC 0.83 clears our target of 0.82. Top-decile precision of 68% means that if we target the riskiest 10% (10K customers), 6,800 of them are actual churners — a good signal-to-noise ratio for an intervention campaign.

---

## Section 6: Eval plan

**Calibration check:**
The model must not just discriminate but also be calibrated — a predicted probability of 0.7 should match actual churn rates in that risk band. I computed a reliability diagram (calibration curve). The model is slightly overconfident at high probabilities — I'd apply isotonic regression calibration before production.

**Threshold analysis:**
| Threshold | Precision | Recall | F1 | Customers targeted |
|-----------|-----------|--------|----|--------------------|
| 0.3 | 52% | 79% | 0.63 | 22,000 |
| 0.5 | 64% | 61% | 0.63 | 11,500 |
| 0.7 | 74% | 38% | 0.50 | 6,200 |

The right threshold depends on the campaign budget. At $5/intervention:
- 0.3 threshold: 22K contacts × $5 = $110K campaign cost. 0.79 × 8,000 churners saved × $200 LTV = $1.26M. ROI: 11.5×.
- 0.7 threshold: 6.2K contacts × $5 = $31K cost. 0.38 × 8,000 = 3,040 churners saved × $200 = $608K. ROI: 19.6×. Better ROI but fewer churners saved.

*I would present both scenarios and ask the business which they prefer: maximize total churners saved or maximize ROI on the campaign budget.*

**Top-5 SHAP feature importances:**
1. `logins_last_30d` (negative: fewer logins → higher churn risk)
2. `tenure_days` (negative: newer customers churn more)
3. `support_contacts_last_90d` (positive: more support contacts → higher churn risk)
4. `monthly_spend` (negative: higher spend → lower churn risk, counterintuitive but makes sense for premium plan loyalty)
5. `plan_tier_encoded` (free → paid conversion customers are stickiest)

These are actionable for the retention team: a new customer (low tenure) who hasn't logged in this month and opened 3 support tickets is the highest-risk profile. That's a specific message to send.

---

## Section 7: Risks

| Risk | Note |
|------|------|
| Leakage | Checked — one feature dropped (`last_contact_date`). No other obvious leakage. |
| Distribution shift | This model was trained on data from [X months]. If product or pricing changes, the feature distributions may shift. Schedule a quarterly model refresh. |
| Intervention bias | If we always intervene on high-risk customers, we can never build a clean counterfactual. Consider an A/B holdout group (5% of high-risk customers receive no intervention) to measure true lift. |
| Calibration | Slightly overconfident at high probabilities. Apply isotonic regression calibration before using predicted probabilities as-is for campaign prioritization. |
| Feature drift | `logins_last_30d` is the top feature. If a product outage causes a dip in logins, the model will spike churn predictions falsely. Add input monitoring on this feature distribution. |

---

## Section 8: Next steps / not done

*This section is mandatory in every take-home. It signals judgment about what matters most.*

**With two more hours:**
1. Threshold calibration using a business cost matrix (false positive cost = $5 wasted campaign spend; false negative cost = $200 LTV lost). Compute the optimal threshold from first principles rather than eyeballing.
2. Segment-level eval: is AUROC consistent across plan tiers and tenure cohorts? A model with AUROC 0.83 overall but 0.61 on new customers would need a separate model or segment-specific calibration.
3. Test a simple neural net (2-layer MLP) on the same holdout set to validate that LightGBM is the right choice and the gap is not material.

**Not done — and why I deprioritized it:**
- Ensemble stacking (LightGBM + LR + neural net) — would likely add 1–2 AUROC points. Deprioritized because the single model already clears the target, and explainability is harder with ensembles.
- Temporal validation — ideally I'd train on months 1–12 and test on month 13, rather than a random split. This would validate that the model generalizes forward in time. Deprioritized due to timebox; I'd do this before production.
- Hyperparameter search beyond manual tuning — Optuna run would likely improve by another 1–2 points. Not worth the timebox investment.

**What I'd want from the business before production:**
- Confirmed cost matrix for threshold setting
- Decision on A/B holdout design
- Approval of model refresh cadence (quarterly recommended)

---

## Memo close

> "The model achieves AUROC 0.83 and top-decile precision of 68% — both above the targets I set. The strongest signal is recent login frequency and tenure, which suggests early-life and disengaged customers are the highest-risk groups. The retention team can target these segments specifically with onboarding-improvement and re-engagement messages, rather than a blunt 'we miss you' campaign.
>
> The most important open question before production is threshold setting: the business needs to weigh campaign ROI (optimize for fewer, higher-confidence contacts) against total churners saved (reach more customers at lower confidence). I've built the analysis to support either choice."
