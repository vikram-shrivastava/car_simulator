import pandas as pd
import numpy as np

# Path to your CSV file
csv_file = r"C:\Users\vikra\Code\car_simulator\data\driving_log.csv"

# Read CSV (assuming space or tab separated)
df = pd.read_csv(csv_file, sep=r'\s+', header=None)

# The last 4 columns are: steering_angle, throttle, reverse, speed
steering = df.iloc[:, -4]
throttle = df.iloc[:, -3]
reverse = df.iloc[:, -2]
speed = df.iloc[:, -1]

def calculate_score(steering, throttle, reverse, speed, prev_speed=None):
    """
    Calculate driving score with safe driving checks:
    - Reward smooth speed (low fluctuation)
    - Reward proper speed range (<= 30 mph)
    - Reward proper steering (low sudden turns)
    - Penalize reverse usage or bad steering
    """
    # Convert inputs to float safely
    steering = float(str(steering).replace(',', ''))
    throttle = float(str(throttle).replace(',', ''))
    reverse = float(str(reverse).replace(',', ''))
    speed = float(str(speed).replace(',', ''))

    score = 0

    # --- Reward for proper speed ---
    SPEED_LIMIT = 30  # max vehicle speed
    if 0 < speed <= SPEED_LIMIT:
        score += (speed / SPEED_LIMIT) * 30  # scale to 0-30 points
    else:
        score -= 10  # penalty for overspeeding

    # --- Penalize rapid speed changes ---
    if prev_speed is not None:
        speed_diff = abs(speed - prev_speed)
        if speed_diff > 5:  # threshold for sudden fluctuation
            score -= speed_diff * 1.0  # penalty for unsafe speed changes
        else:
            score += 3  # small bonus for smooth driving

    # --- Reward proper steering ---
    STEERING_UTURN = 25  # degree
    if abs(steering) < 5:  # smooth lane keeping
        score += 10
    elif abs(steering) <= STEERING_UTURN:  # normal turns / u-turns
        score += 5
    else:  # sharp/bad turn
        score -= abs(steering) * 0.5

    # --- Reward proper throttle usage ---
    score += throttle * 1.0

    # --- Penalize reverse usage ---
    if reverse > 0:
        score -= 5  # small penalty for reverse usage

    return score

# Calculate score with previous speed check for smooth driving
prev_speed = None
scores = []

for i, row in df.iterrows():
    score = calculate_score(row.iloc[-4], row.iloc[-3], row.iloc[-2], row.iloc[-1], prev_speed)
    scores.append(score)
    prev_speed = float(str(row.iloc[-1]).replace(',', ''))  # update prev_speed for next row

df['raw_score'] = scores

# --- Normalize scores to 0-100 ---
max_score_per_row = 50  # max possible points per row if perfectly safe driving
total_max_score = len(df) * max_score_per_row
total_raw_score = sum(scores)

# Normalize
normalized_score = (total_raw_score / total_max_score) * 100
normalized_score = max(0, min(100, normalized_score))  # clamp between 0 and 100

# Optional: add normalized score column (same for all rows)
df['score'] = normalized_score

# Print last 10 raw scores for inspection
print(df[['raw_score']].tail(10))

# Print final driving score out of 100
print(f"Driving Score (out of 100): {normalized_score:.2f}")
