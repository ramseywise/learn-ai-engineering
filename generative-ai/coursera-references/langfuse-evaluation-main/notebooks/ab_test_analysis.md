# A/B Test Analysis Guide

## Overview
This guide explains how to analyze the results of the A/B test comparing v1 (lenient) vs v2 (strict) hallucination detection prompts.

## Running the A/B Test

```bash
# Test on 20 conversations (default)
python ab_test_prompts.py

# Test on custom number
python ab_test_prompts.py --limit 50

# Custom output directory
python ab_test_prompts.py --limit 30 --output-dir ./my_results
```

## Output Files

After running, you'll get 3 files in `./ab_test_results/`:

1. **ab_test_full_TIMESTAMP.json** - Complete results with all data
2. **ab_test_v1_lenient_TIMESTAMP.csv** - V1 results (CSV format)
3. **ab_test_v2_strict_TIMESTAMP.csv** - V2 results (CSV format)

## Analysis in Python

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load results
df_v1 = pd.read_csv('ab_test_results/ab_test_v1_lenient_TIMESTAMP.csv')
df_v2 = pd.read_csv('ab_test_results/ab_test_v2_strict_TIMESTAMP.csv')

# === HALLUCINATION RATE COMPARISON ===

hall_v1 = df_v1['hall_hallucination_detected'].sum() / len(df_v1) * 100
hall_v2 = df_v2['hall_hallucination_detected'].sum() / len(df_v2) * 100

print(f"V1 Hallucination Rate: {hall_v1:.1f}%")
print(f"V2 Hallucination Rate: {hall_v2:.1f}%")
print(f"Difference: {hall_v2 - hall_v1:+.1f}%")

# === SEVERITY COMPARISON ===

severity_v1 = df_v1['hall_severity'].value_counts()
severity_v2 = df_v2['hall_severity'].value_counts()

print("\nV1 Severity Distribution:")
print(severity_v1)

print("\nV2 Severity Distribution:")
print(severity_v2)

# === CRITICAL FINDINGS ===

critical_v1 = df_v1[df_v1['hall_severity'] == 'critical']
critical_v2 = df_v2[df_v2['hall_severity'] == 'critical']

print(f"\nCritical hallucinations V1: {len(critical_v1)}")
print(f"Critical hallucinations V2: {len(critical_v2)}")

# === AGREEMENT ANALYSIS ===

# Merge on session_id
merged = df_v1.merge(
    df_v2,
    on='session_id',
    suffixes=('_v1', '_v2')
)

# Where both agree
both_detected = merged[
    (merged['hall_hallucination_detected_v1'] == True) &
    (merged['hall_hallucination_detected_v2'] == True)
]

# V1 detected but V2 didn't
v1_only = merged[
    (merged['hall_hallucination_detected_v1'] == True) &
    (merged['hall_hallucination_detected_v2'] == False)
]

# V2 detected but V1 didn't
v2_only = merged[
    (merged['hall_hallucination_detected_v1'] == False) &
    (merged['hall_hallucination_detected_v2'] == True)
]

print(f"\nAgreement Analysis:")
print(f"  Both detected: {len(both_detected)}")
print(f"  Only V1 detected: {len(v1_only)}")
print(f"  Only V2 detected: {len(v2_only)}")  # This is the key metric
print(f"  Neither detected: {len(merged) - len(both_detected) - len(v1_only) - len(v2_only)}")

# === VISUALIZATION ===

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: Hallucination Rate
ax1 = axes[0, 0]
rates = pd.DataFrame({
    'Version': ['V1 (Lenient)', 'V2 (Strict)'],
    'Hallucination Rate (%)': [hall_v1, hall_v2]
})
sns.barplot(data=rates, x='Version', y='Hallucination Rate (%)', ax=ax1)
ax1.set_title('Hallucination Detection Rate')
ax1.set_ylim(0, 100)

# Plot 2: Severity Comparison
ax2 = axes[0, 1]
severity_comparison = pd.DataFrame({
    'V1': severity_v1,
    'V2': severity_v2
}).fillna(0)
severity_comparison.plot(kind='bar', ax=ax2)
ax2.set_title('Severity Distribution')
ax2.set_xlabel('Severity')
ax2.set_ylabel('Count')
ax2.legend(['V1 (Lenient)', 'V2 (Strict)'])

# Plot 3: Agreement Matrix
ax3 = axes[1, 0]
agreement_data = [
    [len(both_detected), len(v1_only)],
    [len(v2_only), len(merged) - len(both_detected) - len(v1_only) - len(v2_only)]
]
sns.heatmap(agreement_data, annot=True, fmt='d', cmap='Blues', ax=ax3,
            xticklabels=['V1: Yes', 'V1: No'],
            yticklabels=['V2: Yes', 'V2: No'])
ax3.set_title('Agreement Matrix')

# Plot 4: Critical Cases Only
ax4 = axes[1, 1]
critical_counts = pd.DataFrame({
    'Version': ['V1 (Lenient)', 'V2 (Strict)'],
    'Critical Cases': [len(critical_v1), len(critical_v2)]
})
sns.barplot(data=critical_counts, x='Version', y='Critical Cases', ax=ax4, palette='Reds_r')
ax4.set_title('Critical Hallucinations Detected')

plt.tight_layout()
plt.savefig('ab_test_results/ab_test_comparison.png', dpi=150, bbox_inches='tight')
print("\n✅ Visualization saved: ab_test_results/ab_test_comparison.png")
plt.show()
```

## Key Metrics to Analyze

### 1. **Sensitivity (Detection Rate)**
```python
# How many more hallucinations does V2 detect?
sensitivity_increase = (hall_v2 - hall_v1) / hall_v1 * 100
print(f"V2 is {sensitivity_increase:.1f}% more sensitive")
```

**Expected Result:** V2 should detect 20-50% more hallucinations (more strict)

### 2. **False Positive Risk**
```python
# Cases where V2 detected but V1 didn't - need manual review
print(f"\nCases to review (V2 only): {len(v2_only)}")
for idx, row in v2_only.iterrows():
    print(f"  Session: {row['session_id']}")
    print(f"  V2 Severity: {row['hall_severity_v2']}")
    print(f"  V2 Assessment: {row['hall_overall_assessment_v2'][:100]}...")
    print()
```

**Action:** Manually review these to check if V2 is too strict (false positives)

### 3. **Critical Case Coverage**
```python
# Did V2 catch all critical cases that V1 caught?
critical_sessions_v1 = set(critical_v1['session_id'])
critical_sessions_v2 = set(critical_v2['session_id'])

missed_critical = critical_sessions_v1 - critical_sessions_v2
print(f"Critical cases V1 found but V2 missed: {len(missed_critical)}")
# Should be 0 - V2 should be MORE strict, not less
```

### 4. **Severity Escalation**
```python
# Cases where V2 assigned higher severity than V1
severity_map = {'none': 0, 'minor': 1, 'major': 2, 'critical': 3}

merged['sev_v1_num'] = merged['hall_severity_v1'].map(severity_map)
merged['sev_v2_num'] = merged['hall_severity_v2'].map(severity_map)

escalated = merged[merged['sev_v2_num'] > merged['sev_v1_num']]
print(f"\nCases where V2 assigned higher severity: {len(escalated)}")
print(escalated[['session_id', 'hall_severity_v1', 'hall_severity_v2']])
```

## Decision Criteria

### ✅ Use V2 (Strict) if:
1. V2 detects 20-50% more hallucinations
2. Manual review of "V2 only" cases confirms they ARE hallucinations
3. V2 catches all critical cases that V1 caught + more
4. False positive rate < 10% (based on manual review)

### ⚠️ Keep V1 (Lenient) if:
1. V2 detects >80% more hallucinations (too strict)
2. Manual review shows >20% false positives in "V2 only"
3. V2 misses critical cases that V1 found

### 🔧 Tune V2 if:
1. False positive rate 10-20%
2. Too many MINOR cases flagged as MAJOR/CRITICAL
3. Agreement rate < 60% (prompts too different)

## Expected Results

Based on the "fiducia estructurada" example, V2 should:

```
V1 (Lenient):
- Detects obvious fabrications
- Misses entity substitution cases
- Lower sensitivity to "mixing" hallucinations

V2 (Strict):
- Detects all V1 cases + entity substitution
- Higher severity for contact info errors (CRITICAL)
- Catches applying info from Product A to Product B
```

**Target Agreement:**
- Both detect: 60-70% (core hallucinations)
- V2 only: 20-30% (stricter catches more)
- V1 only: <5% (V2 should catch everything V1 does)
- Neither: 5-10% (clean cases)

## Next Steps

1. Run A/B test: `python ab_test_prompts.py --limit 50`
2. Analyze results with code above
3. Manually review "V2 only" cases (sample 10-20)
4. Calculate false positive rate
5. Decide: Use V2, Keep V1, or Tune V2
6. If using V2, update default in `src/config.py`: `prompt_version: str = "v2"`
