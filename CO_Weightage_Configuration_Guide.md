# CO-wise Assessment Weightage Configuration Guide

This guide explains how to configure the **Attainment Software** using the new **CO-wise Weightage** system. This system ensures that every Course Outcome (CO) is evaluated fairly, regardless of which assessments it appears in.

---

## 1. The Concept

Instead of assigning a global weight to an assessment (e.g., "Internal Exams are worth 30%"), you now assign weights specific to each CO within that assessment.

**Rule of Thumb:**
> For every single CO, the sum of weights across all assessments must be **exactly 1.0**.

### Example Scenario
- **CO1** is tested in both Internal (CCE1) and End Term (ET). You want 50-50 weightage.
- **CO2** is tested more heavily in End Term. You want 30-70 weightage.
- **CO3** is a project-based CO, tested ONLY in the Project assessment.

---

## 2. The `CO_Weightage` Sheet

You must add a new sheet named **`CO_Weightage`** to your `config.xlsx` file.

### Required Columns
1.  **Assessment**: The name of the assessment (must match your Marks file sheet names).
2.  **CO_ID**: The Course Outcome ID (e.g., CO1, CO2).
3.  **Weight**: The weight of that assessment *for that specific CO*.

### Example Table

| Assessment | CO_ID | Weight | Explanation |
| :--- | :--- | :--- | :--- |
| CCE1 | CO1 | 0.5 | 50% of CO1 comes from CCE1 |
| ET | CO1 | 0.5 | 50% of CO1 comes from ET |
| **Total** | **CO1** | **1.0** | **Valid (0.5 + 0.5 = 1.0)** |
| | | | |
| CCE1 | CO2 | 0.3 | 30% of CO2 comes from CCE1 |
| ET | CO2 | 0.7 | 70% of CO2 comes from ET |
| **Total** | **CO2** | **1.0** | **Valid (0.3 + 0.7 = 1.0)** |
| | | | |
| Project | CO3 | 1.0 | 100% of CO3 comes from Project |
| **Total** | **CO3** | **1.0** | **Valid (1.0 = 1.0)** |

---

## 3. Common Errors & Troubleshooting

### Error: "Total weight for 'CO1' is 0.8. It must be exactly 1.0."
**Cause:** The weights you assigned for CO1 do not add up to 1.0.
**Fix:** Check all rows for CO1. Maybe you missed an assessment (e.g., CCE2) or the values are incorrect (e.g., 0.3 + 0.5 = 0.8).

### Error: "Missing weight for Assessment 'CCE1' -> CO 'CO1'"
**Cause:** You have questions in CCE1 mapped to CO1, but you forgot to define a weight for this pair in the `CO_Weightage` sheet.
**Fix:** Add a row for CCE1 + CO1 in the configuration.

### Error: "Missing 'CO_Weightage' sheet"
**Cause:** Your `config.xlsx` is using the old format.
**Fix:** Create the `CO_Weightage` sheet and populate it. You can delete the old `Assessment_Weightage` sheet.

---

## 4. Why This is Better
- **Fairness:** A student isn't penalized if a CO (like a project) is only assessed in one component.
- **Flexibility:** You can have different weight distributions for Theory COs vs. Practical COs.
- **Accuracy:** The attainment percentage is always calculated against the *attempted weight*, ensuring a student getting full marks receives 100% attainment.
