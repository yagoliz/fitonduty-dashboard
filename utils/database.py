# utils/db_utils.py
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from datetime import datetime, timedelta
import numpy as np

# Get database connection string from environment variable or use default for development
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost:5432/dashboard')

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


def get_user_latest_data_date(user_id):
    """
    Get the most recent date where the user has health data
    
    Args:
        user_id: User ID
        
    Returns:
        Date object of the most recent data, or None if no data exists
    """
    query = text("""
        SELECT MAX(date) as latest_date
        FROM health_metrics
        WHERE user_id = :user_id
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()
            
            if row and row[0]:
                return row[0]
            return None
    except Exception as e:
        print(f"Error getting latest data date for user {user_id}: {e}")
        return None
    

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
                hrz.very_light_percent, hrz.light_percent, hrz.moderate_percent, 
                hrz.intense_percent, hrz.beast_mode_percent,
                ms.walking_minutes, ms.walking_fast_minutes, ms.jogging_minutes, ms.running_minutes
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            LEFT JOIN movement_speeds ms ON hm.id = ms.health_metric_id
            WHERE hm.user_id = :user_id 
            AND hm.date BETWEEN :start_date AND :end_date
            ORDER BY hm.date
        """)
        params = {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
        }
    elif start_date:
        query = text("""
            SELECT 
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest,
                hrz.very_light_percent, hrz.light_percent, hrz.moderate_percent, 
                hrz.intense_percent, hrz.beast_mode_percent,
                ms.walking_minutes, ms.walking_fast_minutes, ms.jogging_minutes, ms.running_minutes
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            LEFT JOIN movement_speeds ms ON hm.id = ms.health_metric_id
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
                hrz.very_light_percent, hrz.light_percent, hrz.moderate_percent, 
                hrz.intense_percent, hrz.beast_mode_percent,
                ms.walking_minutes, ms.walking_fast_minutes, ms.jogging_minutes, ms.running_minutes
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            LEFT JOIN movement_speeds ms ON hm.id = ms.health_metric_id
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
                hrz.very_light_percent, hrz.light_percent, hrz.moderate_percent, 
                hrz.intense_percent, hrz.beast_mode_percent,
                ms.walking_minutes, ms.walking_fast_minutes, ms.jogging_minutes, ms.running_minutes
            FROM health_metrics hm
            LEFT JOIN heart_rate_zones hrz ON hm.id = hrz.health_metric_id
            LEFT JOIN movement_speeds ms ON hm.id = ms.health_metric_id
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
    

def get_participant_ranking(user_id, start_date, end_date):
    """
    Get the participant's data consistency ranking within their group
    
    Args:
        user_id: User ID
        start_date: Start date for data range
        end_date: End date for data range
        
    Returns:
        Dictionary with ranking information
    """
    
    query = text("""
        SELECT * FROM get_participant_data_consistency_rank(:user_id, :start_date, :end_date)
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            })
            row = result.fetchone()
            
            if row:
                ranking_data = {}
                for idx, col in enumerate(result.keys()):
                    ranking_data[col] = row[idx]
                return ranking_data
            return None
    except Exception as e:
        print(f"Error getting participant ranking: {e}")
        return None
    

def load_anomaly_data(user_id, date=None, start_date=None, end_date=None):
    """
    Load anomaly score data for a participant
    
    Args:
        user_id: User ID
        date: Specific date to load (optional)
        start_date: Start date for range (optional)
        end_date: End date for range (optional)
        
    Returns:
        Pandas DataFrame with anomaly data
    """
    if date:
        # Single day query
        query = text("""
            SELECT date, time_slot, score, label
            FROM anomaly_scores
            WHERE user_id = :user_id AND date = :date
            ORDER BY time_slot
        """)
        params = {"user_id": user_id, "date": date}
    elif start_date and end_date:
        # Date range query
        query = text("""
            SELECT date, time_slot, score, label
            FROM anomaly_scores
            WHERE user_id = :user_id 
            AND date BETWEEN :start_date AND :end_date
            ORDER BY date, time_slot
        """)
        params = {"user_id": user_id, "start_date": start_date, "end_date": end_date}
    else:
        # Default to latest date
        query = text("""
            SELECT date, time_slot, score, label
            FROM anomaly_scores
            WHERE user_id = :user_id 
            AND date = (
                SELECT MAX(date) FROM anomaly_scores 
                WHERE user_id = :user_id
            )
            ORDER BY time_slot
        """)
        params = {"user_id": user_id}
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params=params)
            
            # Add calculated time column (for easier plotting)
            if not df.empty:
                # Convert time_slot (minutes) to time string
                df['time'] = df['time_slot'].apply(
                    lambda x: f"{x // 60:02d}:{x % 60:02d}"
                )
                
                # Create datetime column for plotting
                df['datetime'] = df.apply(
                    lambda row: pd.Timestamp(
                        row['date'].year, row['date'].month, row['date'].day, 
                        row['time_slot'] // 60, row['time_slot'] % 60
                    ), 
                    axis=1
                )
            
            return df
    except Exception as e:
        print(f"Error loading anomaly data: {e}")
        return pd.DataFrame()