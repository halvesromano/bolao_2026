def calculate_points(prediction, match):
    # 1. Exact Score: 10 points
    if prediction.home_score == match.home_score and prediction.away_score == match.away_score:
        return 10
    
    points = 0
    
    # 2. Correct Winner/Draw: 3 points
    pred_diff = prediction.home_score - prediction.away_score
    real_diff = match.home_score - match.away_score
    
    # Check if sign matches (positive, negative, or zero)
    if (pred_diff > 0 and real_diff > 0) or \
       (pred_diff < 0 and real_diff < 0) or \
       (pred_diff == 0 and real_diff == 0):
        points += 3
        
    # 3. Exact Goals of ONE team: 3 points
    # Since we already handled Exact Score (both correct), this runs only if NOT exact score.
    # So it implies only one can be correct, or none.
    # If both were correct, we would have returned 10.
    # So we just check if home is correct OR away is correct.
    if prediction.home_score == match.home_score or prediction.away_score == match.away_score:
        points += 3
        
    return points
