# utils/data_utils.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def load_participant_data(participant_id, date=None):
    """
    Load participant data for a specific date or date range
    
    Args:
        participant_id: The ID of the participant
        date: The date to load data for, or None for recent data
    
    Returns:
        A pandas DataFrame with the participant data
    """
    # In a real implementation, this would query a database
    # For now, generate some simulated data
    
    # If no date is provided, use the current date
    if date is None:
        # Use current date for consistency
        end_date = datetime.now().date()
        # Generate data for the last 7 days
        start_date = end_date - timedelta(days=6)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    else:
        # Parse the date string if it's a string
        if isinstance(date, str):
            date = pd.to_datetime(date).date()
        # Use a single date
        date_range = pd.date_range(start=date, periods=1, freq='D')
    
    # Create simulated data
    data = []
    
    # Use participant_id as seed for reproducible random data
    random.seed(hash(participant_id))
    
    for current_date in date_range:
        # Generate daily metrics with some variability based on participant
        baseline_hr = random.randint(55, 75)  # Different baseline for each participant
        baseline_sleep = 7.5 + random.uniform(-0.5, 0.5)  # Different baseline sleep
        
        # Create a row of data for this day
        row = {
            'date': current_date,
            'resting_hr': baseline_hr + random.uniform(-3, 3),
            'max_hr': baseline_hr + 80 + random.uniform(-10, 10),
            'avg_hr': baseline_hr + 25 + random.uniform(-8, 8),
            'sleep_hours': baseline_sleep + random.uniform(-1, 1),
            'deep_sleep_hours': (baseline_sleep + random.uniform(-1, 1)) * 0.25,
            'rem_sleep_hours': (baseline_sleep + random.uniform(-1, 1)) * 0.2,
            'light_sleep_hours': (baseline_sleep + random.uniform(-1, 1)) * 0.55,
            'steps': random.randint(5000, 15000),
            'calories': random.randint(1800, 3000),
            'activity_score': random.randint(30, 95),
            'hrv_rest': random.randint(30, 70),
            'stress_score': random.randint(20, 80),
            'recovery_score': random.randint(30, 95),
        }
        
        # Add heart rate zone percentages (should sum to 100%)
        zone_percentages = generate_zone_percentages()
        for i, pct in enumerate(zone_percentages):
            row[f'zone{i+1}_percent'] = pct
        
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Return empty DataFrame if no data is available
    if df.empty:
        return pd.DataFrame()
    
    return df

def generate_zone_percentages(num_zones=7):
    """
    Generate random percentages for heart rate zones that sum to 100%
    
    Args:
        num_zones: Number of zones to generate
    
    Returns:
        List of percentages
    """
    # Generate random values
    values = [random.random() for _ in range(num_zones)]
    
    # Normalize to sum to 100
    total = sum(values)
    percentages = [100 * (v / total) for v in values]
    
    # Ensure they sum to exactly 100% (handle rounding errors)
    percentages[-1] = 100 - sum(percentages[:-1])
    
    return percentages