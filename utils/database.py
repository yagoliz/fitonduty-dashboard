# utils/db_utils.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from datetime import datetime, timedelta
import numpy as np

# Get database connection string from environment variable or use default for development
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost:5432/health_dashboard')

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600  # Recycle connections after 1 hour
)

def get_user_by_id(user_id):
    """Get user by username from the database"""
    query = text("""
        SELECT id, username, password_hash, role, last_login, is_active 
        FROM users 
        WHERE id = :user_id AND is_active = TRUE
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        user_data = result.fetchone()

    if user_data is None:
        return None
    
    user_dict = {}
    for idx, col in enumerate(result.keys()):
        user_dict[col] = user_data[idx]
        
    return user_dict

def get_user_by_username(username):
    """Get user by username from the database"""
    query = text("""
        SELECT id, username, password_hash, role, last_login, is_active 
        FROM users 
        WHERE username = :username AND is_active = TRUE
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"username": username})
        user_data = result.fetchone()

    if user_data is None:
        return None
    
    user_dict = {}
    for idx, col in enumerate(result.keys()):
        user_dict[col] = user_data[idx]
        
    return user_dict

def get_user_groups(user_id):
    """Get groups for a specific user"""
    query = text("""
        SELECT g.id, g.group_name, g.description
        FROM groups g
        JOIN user_groups ug ON g.id = ug.group_id
        WHERE ug.user_id = :user_id
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        groups = []
        for row in result:
            group_dict = {}
            for idx, col in enumerate(result.keys()):
                group_dict[col] = row[idx]
            groups.append(group_dict)
        
    return groups

def update_last_login(user_id):
    """Update the last login timestamp for a user"""
    query = text("""
        UPDATE users 
        SET last_login = CURRENT_TIMESTAMP 
        WHERE id = :user_id
    """)
    
    with engine.connect() as conn:
        conn.execute(query, {"user_id": user_id})
        conn.commit()

def create_session(user_id, session_token, ip_address, user_agent, expires_at):
    """Create a new session record"""
    query = text("""
        INSERT INTO sessions (user_id, session_token, ip_address, user_agent, expires_at)
        VALUES (:user_id, :session_token, :ip_address, :user_agent, :expires_at)
    """)
    
    with engine.connect() as conn:
        conn.execute(query, {
            "user_id": user_id,
            "session_token": session_token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "expires_at": expires_at
        })
        conn.commit()

def get_participants_by_group(group_id=None):
    """Get all participants grouped by their group"""
    if group_id:
        query = text("""
            SELECT u.id, u.username, g.id as group_id, g.group_name
            FROM users u
            JOIN user_groups ug ON u.id = ug.user_id
            JOIN groups g ON ug.group_id = g.id
            WHERE u.role = 'participant' AND g.id = :group_id
            ORDER BY u.username
        """)
        params = {"group_id": group_id}
    else:
        query = text("""
            SELECT u.id, u.username, g.id as group_id, g.group_name
            FROM users u
            JOIN user_groups ug ON u.id = ug.user_id
            JOIN groups g ON ug.group_id = g.id
            WHERE u.role = 'participant'
            ORDER BY g.group_name, u.username
        """)
        params = {}
    
    with engine.connect() as conn:
        result = conn.execute(query, params)
        user_data = result.fetchall()

        if user_data is None:
            return None

        participants = []
        for row in user_data:
            user_dict = {}
            for idx, col in enumerate(result.keys()):
                user_dict[col] = row[idx]
            participants.append(user_dict)
    
    # Organize by group
    groups = {}
    for p in participants:
        group_id = p['group_id']
        if group_id not in groups:
            groups[group_id] = {
                'name': p['group_name'],
                'participants': []
            }
        groups[group_id]['participants'].append({
            'id': p['id'],
            'username': p['username'],
        })
    
    return groups

def get_all_groups():
    """Get list of all groups"""
    query = text("""
        SELECT id, group_name as name, description
        FROM groups
        ORDER BY group_name
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        group_data = result.fetchall()

    if group_data is None:
        return None
    
    group_list = []
    for row in group_data:
        group_dict = {}
        for idx, col in enumerate(result.keys()):
            group_dict[col] = row[idx]
        group_list.append(group_dict)
    
    return group_list

def load_participant_data(user_id, start_date=None, end_date=None):
    """
    Load health data for a participant from the database
    
    Args:
        user_id: User ID
        start_date: Start date for data range (optional)
        end_date: End date for data range (optional)
        
    Returns:
        Pandas DataFrame with health data
    """
    # Build the query based on date parameters
    if start_date and end_date:
        query = text("""
            SELECT 
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest,
                hrz.zone1_percent, hrz.zone2_percent, hrz.zone3_percent, 
                hrz.zone4_percent, hrz.zone5_percent, hrz.zone6_percent, 
                hrz.zone7_percent
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            WHERE hm.user_id = :user_id 
            AND hm.date BETWEEN :start_date AND :end_date
            ORDER BY hm.date
        """)
        params = {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }
    elif start_date:
        query = text("""
            SELECT 
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest,
                hrz.zone1_percent, hrz.zone2_percent, hrz.zone3_percent, 
                hrz.zone4_percent, hrz.zone5_percent, hrz.zone6_percent, 
                hrz.zone7_percent
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            WHERE hm.user_id = :user_id 
            AND hm.date >= :start_date
            ORDER BY hm.date
        """)
        params = {
            "user_id": user_id,
            "start_date": start_date
        }
    elif end_date:
        query = text("""
            SELECT 
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest,
                hrz.zone1_percent, hrz.zone2_percent, hrz.zone3_percent, 
                hrz.zone4_percent, hrz.zone5_percent, hrz.zone6_percent, 
                hrz.zone7_percent
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            WHERE hm.user_id = :user_id 
            AND hm.date <= :end_date
            ORDER BY hm.date
        """)
        params = {
            "user_id": user_id,
            "end_date": end_date
        }
    else:
        # If no dates provided, get last 30 days
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=30)
        query = text("""
            SELECT 
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest,
                hrz.zone1_percent, hrz.zone2_percent, hrz.zone3_percent, 
                hrz.zone4_percent, hrz.zone5_percent, hrz.zone6_percent, 
                hrz.zone7_percent
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            WHERE hm.user_id = :user_id 
            AND hm.date >= :thirty_days_ago
            ORDER BY hm.date
        """)
        params = {
            "user_id": user_id,
            "thirty_days_ago": thirty_days_ago
        }
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Error loading data from database: {e}")
        return pd.DataFrame()  # Return empty dataframe on error

def save_health_metrics(user_id, date, metrics):
    """
    Save health metrics for a user
    
    Args:
        user_id: User ID
        date: Date for the metrics
        metrics: Dictionary with health metrics data
    """
    # First insert or update the health_metrics record
    upsert_metrics_query = text("""
        INSERT INTO health_metrics 
            (user_id, date, resting_hr, max_hr, sleep_hours, hrv_rest)
        VALUES 
            (:user_id, :date, :resting_hr, :max_hr, :sleep_hours, :hrv_rest)
        ON CONFLICT (user_id, date) 
        DO UPDATE SET
            resting_hr = :resting_hr,
            max_hr = :max_hr,
            sleep_hours = :sleep_hours,
            hrv_rest = :hrv_rest,
            created_at = CURRENT_TIMESTAMP
        RETURNING id
    """)
    
    # Then insert or update the heart rate zones
    upsert_zones_query = text("""
        INSERT INTO heart_rate_zones
            (health_metric_id, zone1_percent, zone2_percent, zone3_percent, 
             zone4_percent, zone5_percent, zone6_percent, zone7_percent)
        VALUES
            (:health_metric_id, :zone1_percent, :zone2_percent, :zone3_percent,
             :zone4_percent, :zone5_percent, :zone6_percent, :zone7_percent)
        ON CONFLICT (health_metric_id)
        DO UPDATE SET
            zone1_percent = :zone1_percent,
            zone2_percent = :zone2_percent,
            zone3_percent = :zone3_percent,
            zone4_percent = :zone4_percent,
            zone5_percent = :zone5_percent,
            zone6_percent = :zone6_percent,
            zone7_percent = :zone7_percent
    """)
    
    try:
        with engine.begin() as conn:  # Use transaction
            # Insert or update health metrics
            metrics_result = conn.execute(
                upsert_metrics_query,
                {
                    "user_id": user_id,
                    "date": date,
                    "resting_hr": metrics.get('resting_hr'),
                    "max_hr": metrics.get('max_hr'),
                    "sleep_hours": metrics.get('sleep_hours'),
                    "hrv_rest": metrics.get('hrv_rest'),
                }
            )
            
            # Get the health metric ID
            health_metric_id = metrics_result.fetchone()[0]
            
            # Insert or update heart rate zones if provided
            if all(f'zone{i}_percent' in metrics for i in range(1, 8)):
                conn.execute(
                    upsert_zones_query,
                    {
                        "health_metric_id": health_metric_id,
                        "zone1_percent": metrics.get('zone1_percent', 0),
                        "zone2_percent": metrics.get('zone2_percent', 0),
                        "zone3_percent": metrics.get('zone3_percent', 0),
                        "zone4_percent": metrics.get('zone4_percent', 0),
                        "zone5_percent": metrics.get('zone5_percent', 0),
                        "zone6_percent": metrics.get('zone6_percent', 0),
                        "zone7_percent": metrics.get('zone7_percent', 0)
                    }
                )
            
        return True
    except Exception as e:
        print(f"Error saving health metrics: {e}")
        return False

def import_mock_data(user_id, start_date, end_date, overwrite=False):
    """
    Generate and import mock data for a user in the given date range
    
    Args:
        user_id: User ID
        start_date: Start date (can be string or date object)
        end_date: End date (can be string or date object)
        overwrite: Whether to overwrite existing data (default: False)
    """
    # Convert string dates to datetime objects if needed
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Calculate the number of days in the range
    delta = end_date - start_date
    days = delta.days + 1
    
    # Create date range
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    
    # Generate data specific to the user (using user_id as seed for consistency)
    np.random.seed(hash(str(user_id)) % 2**32)
    
    # Generate base values for this user
    resting_hr_base = np.random.randint(55, 70)
    max_hr_base = np.random.randint(140, 180)
    sleep_base = np.random.uniform(6.5, 8.5)
    hrv_base = np.random.randint(40, 80)
    
    # If not overwriting, get existing dates to skip
    skip_dates = set()
    if not overwrite:
        query = text("""
            SELECT date FROM health_metrics
            WHERE user_id = :user_id AND date BETWEEN :start_date AND :end_date
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id, "start_date": start_date, "end_date": end_date})
            skip_dates = {row[0] for row in result}
    
    # Process each date in the range
    for date in date_range:
        # Skip if we already have data for this date and not overwriting
        if date in skip_dates:
            continue
        
        # Generate metrics for this date
        metrics = {
            'resting_hr': resting_hr_base + np.random.randint(-5, 6),
            'max_hr': max_hr_base + np.random.randint(-10, 11),
            'sleep_hours': max(0, sleep_base + np.random.normal(0, 0.7)),
            'hrv_rest': max(10, hrv_base + np.random.randint(-15, 16)),
        }
        
        # Generate heart rate zone percentages
        zone_values = []
        for i in range(1, 8):
            if i <= 3:
                base_pct = 20.0  # Higher percentage for lower zones
            else:
                base_pct = 8.0   # Lower percentage for higher zones
                
            zone_values.append(max(0, min(100, base_pct + np.random.normal(0, 5))))
        
        # Normalize to sum to 100%
        zone_sum = sum(zone_values)
        if zone_sum > 0:
            zone_values = [v / zone_sum * 100 for v in zone_values]
        
        # Add zones to metrics
        for i, value in enumerate(zone_values, 1):
            metrics[f'zone{i}_percent'] = value
        
        # Save to database
        save_health_metrics(user_id, date, metrics)
    
    return True