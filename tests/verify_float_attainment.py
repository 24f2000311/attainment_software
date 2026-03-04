import pandas as pd
from services.co_attainment import determine_attainment_level

def test_determine_attainment_level():
    # Mock targets_df mimicking User's Excel sheet
    data = {
        "Level": [3, 2, 1],
        "Min_Students_%": [70.0, 60.0, 50.0]
    }
    targets_df = pd.DataFrame(data)

    test_cases = [
        (40.0, 0.8), # 40/50 = 0.8
        (50.0, 1.01), # exact boundary 
        (55.0, 1.50), # 1.01 + 0.99 * 5/10 = 1.01 + 0.495 = 1.505 -> 1.51
        (60.0, 2.01), # exact boundary
        (65.0, 2.51), # 2.01 + 0.99 * 5/10 = 2.505 -> 2.51
        (70.0, 3.0), # max threshold
        (85.0, 3.0), # above max threshold
        (0.0, 0.0), # base
    ]

    print("Testing determine_attainment_level:")
    print("-----------------------------------")
    
    passed = True
    for x, expected in test_cases:
        result = determine_attainment_level(x, targets_df)
        print(f"Percentage: {x}% -> Expected: {expected}, Got: {result}")
        if abs(result - expected) > 0.01:
            print(f"  [X] MISMATCH! Expected {expected}, but got {result}")
            passed = False
            
    if passed:
        print("\nAll test cases PASSED!")
    else:
        print("\nSome test cases FAILED.")
        
if __name__ == "__main__":
    test_determine_attainment_level()
