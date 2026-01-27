# Attainment Software - User Guide

## Getting Started

1.  **Launch the Application**: Run `desktop_app.py` (or the executable if built).
2.  **Home Screen**: You will see options to upload files or proceed if already loaded.

## Workflow

1.  **Upload Configuration & Marks**:
    *   **Config File**: Excel file containing COs, POs, Targets, and Mapping.
    *   **Marks File**: Excel file containing student marks per assessment.
    *   **Note**: Assessment weights in `Assessment_Weightage` must sum to **1.0** (e.g., 0.3, 0.7). Do not use integers like 30, 70.

2.  **Validation**:
    *   The system checks for structural errors and correct weighting.
    *   If successful, you will see a success message.

3.  **CO Attainment**:
    *   View detailed attainment levels for each CO.
    *   See the weighted breakdown (Direct vs Indirect).
    *   Check "CO Numeric Scores" for granular student performance analysis to see the average performance of the class.

4.  **PO Attainment**:
    *   View calculated PO attainment based on CO levels and mapping strength.

5.  **CQI & Gap Analysis**:
    *   The system automatically identifies COs that failed to meet the target level (default Level 2).
    *   Enter action plans for these "Weak COs".

6.  **Reports**:
    *   Generate PDF or Excel reports containing all analysis and graphs.

## Troubleshooting

*   **"Not Attained" despite high marks?**: Check if the assessment weights cover the full courses. Scores are absolute (relative to total course).
*   **Weights Error**: Ensure weights are decimals (e.g. 0.2) not integers (20).

## Support
For technical issues, fill the form https://forms.gle/NQ5b3gXhZQkiEtfo9
