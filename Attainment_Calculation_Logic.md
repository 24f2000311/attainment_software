# Attainment Calculation Logic & System Overview

This document explains how the software processes data to calculate Course Outcome (CO) and Program Outcome (PO) attainment. It details the data flow, the specific formulas used, and important configuration requirements.

## 1. System Overview

The Attainment Software automates the calculation of OBE (Outcome Based Education) metrics. The high-level workflow is:

1.  **Configuration**: User defines COs, POs, Mappings, Assessment Weights, and Targets.
2.  **Data Ingestion**: User uploads student marks (Excel).
3.  **Processing**: The system normalizes marks, applies weights, and aggregates scores per CO.
4.  **Attainment Calculation**: Scores are compared against targets to determine attainment levels.
5.  **Reporting**: PDF/Excel reports are generated.

## 2. Input Data & Validation

The system relies on strict validation of input data to ensure calculation integrity.

*   **Config Sheets**: Must include `CO_List`, `PO_List`, `CO_PO_Mapping`, `Assessment_Weightage`, `Attainment_Targets`, `Question_CO_Map`, and `Settings`.
*   **Assessment Weights**: The weights defined in `Assessment_Weightage` **MUST sum to exactly 1.0** (within a small margin of error) for each Mode (Direct/Indirect).
    *   *Example*: Internal: 0.3, EndSem: 0.7 (Total 1.0).
    *   *Note*: Integer weights (e.g., 30, 70) are **not allowed** and will raise a validation error.

## 3. CO Attainment Calculation

The Course Outcome attainment is calculated in several steps.

### 3.1 Normalization & Weighting

For every question answered by a student, the system calculates a weighted score based on the **CO-specific Assessment Weight**.

**New Architecture:**
*   Weights are defined per **(Assessment, CO)** pair in `CO_Weightage` sheet.
*   For each CO, the sum of weights across all assessments **must be exactly 1.0**.

**Formula per Question:**
$$ Score_{Question} = \left( \frac{Marks Obtained}{Max Marks} \right) \times Weight_{Assessment, CO} $$

### 3.2 Aggregation (CO Score)

The system sums the weighted scores for all questions mapped to a specific CO for a student.
Since the weights for a CO already sum to 1.0, **no further normalization is needed**.

**Formula per Student-CO:**
$$ Score_{CO} = \sum Score_{Question} $$

> **Note**: This ensures that if a student scores full marks in all assessments for a CO, their final score is exactly 100% (or 1.0).

### 3.3 Percentage Conversion

The raw aggregated score (0.0 - 1.0 scale) is converted to a percentage (0 - 100).

$$ Achieved \%_{Student} = Score_{CO} \times 100 $$

### 3.4 Attainment Level Determination

1.  **Metric**: The system calculates the percentage of students who scored above a "Target Threshold" (defined in `Attainment_Targets` as `Min_Marks_%`).
    *   *Example*: If `Min_Marks_%` is 60, the system counts how many students have an `Achieved %` >= 60.
    *   *Implication*: Since scoring is absolute (relative to total course), COs that are not assessed across the entire weight of the course (e.g., only in Internals) may have low scores that never reach the passing threshold.

2.  **Level Lookup**:
    *   The percentage of students passing the threshold is compared against the `Attainment_Targets` levels.
    *   *Example*:
        *   Level 3: > 70% of students.
        *   Level 2: > 60% of students.
        *   Level 1: > 50% of students.

### 3.5 Weighted Direct/Indirect Attainment

If "Indirect" assessments are configured:

1.  Separate Attainment Levels are calculated for **Direct** and **Indirect** scores.
2.  **Final CO Attainment** is a weighted average of the **Achieved Percentages** (not the Levels), typically 80% Direct + 20% Indirect.
    *   $$ Final \% = (Direct \% \times 0.8) + (Indirect \% \times 0.2) $$
3.  The `Final Level` is looked up using this weighted percentage.

## 4. PO Attainment Calculation

Program Outcome (PO) attainment is derived from the calculated Final CO Attainment Levels.

**Formula:**
$$ PO Value = \frac{\sum (CO Level \times Correlation Strength)}{\sum Correlation Strength} $$

*   **CO Level**: The final attainment level (0-3) of the CO.
*   **Correlation Strength**: The mapping value (1, 2, 3) from `CO_PO_Mapping`.

The result is rounded to 2 decimal places.

## 5. Summary of Key Behaviors

| Behavior | Description |
| :--- | :--- |
| **Weights** | Must be decimals (0.0 - 1.0) summing to 1.0. |
| **Scoring** | Absolute relative to total course (1.0). A student getting 100% in a 30% weight exam gets a score of 30. |
| **Pass/Fail** | A student "Passes" a CO only if their *Weighted Course Score* for that CO exceeds the target (e.g. 60). |
| **Multiple Questions** | If multiple questions in one assessment map to the same CO, their weighted contributions are **added**. This can inflate scores if not carefully mapped. |
