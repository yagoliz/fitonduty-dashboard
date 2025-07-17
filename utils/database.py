from datetime import datetime, timedelta
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

from .logging_config import get_logger

logger = get_logger(__name__)

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
    
    # If user_id is "all", return None
    if user_id == "all":
        return None

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
    # If user_id is "all" return None
    if user_id == "all":
        return None

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
        logger.error(f"Error getting latest data date for user {user_id}: {e}")
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
    # If user_id is "all", return empty DataFrame
    if user_id == "all":
        return pd.DataFrame()

    # Build the query based on date parameters
    if start_date and end_date:
        query = text("""
            SELECT 
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest, hm.step_count,
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
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest, hm.step_count,
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
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest, hm.step_count,
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
                hm.date, hm.resting_hr, hm.max_hr, hm.sleep_hours, hm.hrv_rest, hm.step_count,
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
        logger.error(f"Error loading data from database: {e}")
        return pd.DataFrame()  # Return empty dataframe on error


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
        logger.error(f"Error getting participant ranking: {e}")
        return None
    

def get_all_group_participants_ranking(user_id, start_date, end_date):
    """
    Get ranking data for all participants in the user's group
    
    Args:
        user_id: User ID to determine the group
        start_date: Start date for data range
        end_date: End date for data range
        
    Returns:
        List of dictionaries with all participants' ranking data
    """
    
    query = text("""
        SELECT * FROM get_group_participants_ranking(:user_id, :start_date, :end_date)
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            })
            
            participants_data = []
            for row in result:
                participant_dict = {}
                for idx, col in enumerate(result.keys()):
                    participant_dict[col] = row[idx]
                participants_data.append(participant_dict)
                
            return participants_data
    except Exception as e:
        logger.error(f"Error getting group participants ranking: {e}")
        return []
    

def get_group_historical_data(user_id, start_date, end_date):
    """
    Get historical data for all participants in the user's group
    
    Args:
        user_id: User ID to determine the group
        start_date: Start date for data range
        end_date: End date for data range
        
    Returns:
        DataFrame with historical data for ranking calculations
    """
    
    query = text("""
        SELECT * FROM get_group_historical_data(:user_id, :start_date, :end_date)
    """)
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            })
        return df
    except Exception as e:
        logger.error(f"Error getting group historical data: {e}")
        return pd.DataFrame()
    

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
    # If user_id is "all", return empty DataFrame
    if user_id == "all":
        return pd.DataFrame()

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
        logger.error(f"Error loading anomaly data: {e}")
        return pd.DataFrame()
    

def load_questionnaire_data(user_id, start_date=None, end_date=None):
    """
    Load questionnaire data for a participant from the database
    
    Args:
        user_id: User ID
        start_date: Start date for data range (optional)
        end_date: End date for data range (optional)
        
    Returns:
        Pandas DataFrame with questionnaire data
    """
    # If user_id is "all", return empty DataFrame
    if user_id == "all":
        return pd.DataFrame()

    # Build the query based on date parameters
    if start_date and end_date:
        query = text("""
            SELECT 
                qd.date, qd.perceived_sleep_quality, qd.fatigue_level, 
                qd.motivation_level, qd.created_at
            FROM questionnaire_data qd
            WHERE qd.user_id = :user_id 
            AND qd.date BETWEEN :start_date AND :end_date
            ORDER BY qd.date
        """)
        params = {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
        }
    elif start_date:
        query = text("""
            SELECT 
                qd.date, qd.perceived_sleep_quality, qd.fatigue_level, 
                qd.motivation_level, qd.created_at
            FROM questionnaire_data qd
            WHERE qd.user_id = :user_id 
            AND qd.date >= :start_date
            ORDER BY qd.date
        """)
        params = {
            "user_id": user_id,
            "start_date": start_date
        }
    elif end_date:
        query = text("""
            SELECT 
                qd.date, qd.perceived_sleep_quality, qd.fatigue_level, 
                qd.motivation_level, qd.created_at
            FROM questionnaire_data qd
            WHERE qd.user_id = :user_id 
            AND qd.date <= :end_date
            ORDER BY qd.date
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
                qd.date, qd.perceived_sleep_quality, qd.fatigue_level, 
                qd.motivation_level, qd.created_at
            FROM questionnaire_data qd
            WHERE qd.user_id = :user_id 
            AND qd.date >= :thirty_days_ago
            ORDER BY qd.date
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
        logger.error(f"Error loading questionnaire data from database: {e}")
        return pd.DataFrame()  # Return empty dataframe on error
    

def get_participant_questionnaire_ranking(user_id, start_date, end_date):
    """
    Get the participant's questionnaire completion ranking within their group
    
    Args:
        user_id: User ID
        start_date: Start date for data range
        end_date: End date for data range
        
    Returns:
        Dictionary with questionnaire ranking information
    """
    
    query = text("""
        SELECT * FROM get_participant_questionnaire_rank(:user_id, :start_date, :end_date)
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
        logger.error(f"Error getting participant questionnaire ranking: {e}")
        return None


def get_all_group_questionnaire_ranking(user_id, start_date, end_date):
    """
    Get questionnaire ranking data for all participants in the user's group
    
    Args:
        user_id: User ID to determine the group
        start_date: Start date for data range
        end_date: End date for data range
        
    Returns:
        List of dictionaries with all participants' questionnaire ranking data
    """
    
    query = text("""
        SELECT * FROM get_group_questionnaire_ranking(:user_id, :start_date, :end_date)
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            })
            
            participants_data = []
            for row in result:
                participant_dict = {}
                for idx, col in enumerate(result.keys()):
                    participant_dict[col] = row[idx]
                participants_data.append(participant_dict)
                
            return participants_data
    except Exception as e:
        logger.error(f"Error getting group questionnaire ranking: {e}")
        return []


def get_supervisor_group_data(user_id, start_date, end_date):
    """
    Get aggregated data for a supervisor's assigned group
    
    Args:
        user_id: Supervisor's user ID
        start_date: Start date for data range
        end_date: End date for data range
        
    Returns:
        DataFrame with daily aggregated metrics and data counts
    """
    query = text("""
        WITH supervisor_group AS (
            SELECT g.id as group_id, g.group_name
            FROM groups g
            JOIN user_groups ug ON g.id = ug.group_id
            WHERE ug.user_id = :user_id
            LIMIT 1
        ),
        group_participants AS (
            SELECT u.id as user_id, u.username, sg.group_id, sg.group_name
            FROM users u
            JOIN user_groups ug ON u.id = ug.user_id
            JOIN supervisor_group sg ON ug.group_id = sg.group_id
            WHERE u.role = 'participant'
        ),
        daily_health_aggregates AS (
            SELECT 
                hm.date,
                gp.group_id,
                gp.group_name,
                COUNT(DISTINCT hm.user_id) as physio_data_count,
                AVG(hm.resting_hr) as avg_resting_hr,
                AVG(hm.max_hr) as avg_max_hr,
                AVG(hm.sleep_hours) as avg_sleep_hours,
                AVG(hm.hrv_rest) as avg_hrv_rest,
                AVG(hm.step_count) as avg_step_count
            FROM health_metrics hm
            JOIN group_participants gp ON hm.user_id = gp.user_id
            WHERE hm.date BETWEEN :start_date AND :end_date
            GROUP BY hm.date, gp.group_id, gp.group_name
        ),
        daily_questionnaire_aggregates AS (
            SELECT 
                qd.date,
                gp.group_id,
                gp.group_name,
                COUNT(DISTINCT qd.user_id) as questionnaire_data_count,
                AVG(qd.perceived_sleep_quality) as avg_sleep_quality,
                AVG(qd.fatigue_level) as avg_fatigue_level,
                AVG(qd.motivation_level) as avg_motivation_level
            FROM questionnaire_data qd
            JOIN group_participants gp ON qd.user_id = gp.user_id
            WHERE qd.date BETWEEN :start_date AND :end_date
            GROUP BY qd.date, gp.group_id, gp.group_name
        )
        SELECT 
            COALESCE(dha.date, dqa.date) as date,
            COALESCE(dha.group_id, dqa.group_id) as group_id,
            COALESCE(dha.group_name, dqa.group_name) as group_name,
            COALESCE(dha.physio_data_count, 0) as physio_data_count,
            COALESCE(dqa.questionnaire_data_count, 0) as questionnaire_data_count,
            dha.avg_resting_hr,
            dha.avg_max_hr,
            dha.avg_sleep_hours,
            dha.avg_hrv_rest,
            dha.avg_step_count,
            dqa.avg_sleep_quality,
            dqa.avg_fatigue_level,
            dqa.avg_motivation_level
        FROM daily_health_aggregates dha
        FULL OUTER JOIN daily_questionnaire_aggregates dqa 
            ON dha.date = dqa.date AND dha.group_id = dqa.group_id
        ORDER BY date
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            })
            
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
    except Exception as e:
        logger.error(f"Error getting supervisor group data: {e}")
        return pd.DataFrame()


def get_supervisor_group_info(user_id):
    """
    Get supervisor's assigned group information
    
    Args:
        user_id: Supervisor's user ID
        
    Returns:
        Dictionary with group information
    """
    query = text("""
        SELECT g.id, g.group_name, g.description
        FROM groups g
        JOIN user_groups ug ON g.id = ug.group_id
        WHERE ug.user_id = :user_id
        LIMIT 1
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()
            
            if row:
                group_info = {}
                for idx, col in enumerate(result.keys()):
                    group_info[col] = row[idx]
                return group_info
            return None
    except Exception as e:
        logger.error(f"Error getting supervisor group info: {e}")
        return None


def get_supervisor_group_participants(user_id):
    """
    Get list of participants in supervisor's assigned group
    
    Args:
        user_id: Supervisor's user ID
        
    Returns:
        List of participant dictionaries
    """
    query = text("""
        SELECT u.id, u.username, u.display_name
        FROM users u
        JOIN user_groups ug ON u.id = ug.user_id
        JOIN (
            SELECT g.id as group_id
            FROM groups g
            JOIN user_groups ug2 ON g.id = ug2.group_id
            WHERE ug2.user_id = :user_id
            LIMIT 1
        ) sg ON ug.group_id = sg.group_id
        WHERE u.role = 'participant'
        ORDER BY u.username
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            
            participants = []
            for row in result:
                participant_dict = {}
                for idx, col in enumerate(result.keys()):
                    participant_dict[col] = row[idx]
                participants.append(participant_dict)
                
            return participants
    except Exception as e:
        logger.error(f"Error getting supervisor group participants: {e}")
        return []


def get_group_data_summary(selected_date):
    """
    Get summary of physiological and questionnaire data for all groups for a specific date.
    Returns data counts for Past 7 Days and Past 30 Days from the selected date.
    """
    try:
        # Convert selected_date to datetime if it's a string
        if isinstance(selected_date, str):
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        
        # Calculate date ranges
        past_7_start = selected_date - timedelta(days=6)  # 7 days including selected date
        past_30_start = selected_date - timedelta(days=29)  # 30 days including selected date
        
        query = text("""
            WITH group_summary AS (
                SELECT 
                    g.id as group_id,
                    g.group_name,
                    -- Current day physiological data count
                    COUNT(DISTINCT CASE 
                        WHEN hm_current.date = :selected_date 
                        THEN hm_current.user_id 
                    END) as physio_current_day_count,
                    -- Current day questionnaire data count
                    COUNT(DISTINCT CASE 
                        WHEN qd_current.date = :selected_date 
                        THEN qd_current.user_id 
                    END) as questionnaire_current_day_count,
                    -- Past 7 days physiological data count
                    COUNT(DISTINCT CASE 
                        WHEN hm7.date BETWEEN :past_7_start AND :selected_date 
                        THEN hm7.user_id 
                    END) as physio_7_day_count,
                    -- Past 30 days physiological data count
                    COUNT(DISTINCT CASE 
                        WHEN hm30.date BETWEEN :past_30_start AND :selected_date 
                        THEN hm30.user_id 
                    END) as physio_30_day_count,
                    -- Past 7 days questionnaire data count
                    COUNT(DISTINCT CASE 
                        WHEN qd7.date BETWEEN :past_7_start AND :selected_date 
                        THEN qd7.user_id 
                    END) as questionnaire_7_day_count,
                    -- Past 30 days questionnaire data count
                    COUNT(DISTINCT CASE 
                        WHEN qd30.date BETWEEN :past_30_start AND :selected_date 
                        THEN qd30.user_id 
                    END) as questionnaire_30_day_count,
                    -- Total participants in group
                    COUNT(DISTINCT u.id) as total_participants
                FROM groups g
                JOIN user_groups ug ON g.id = ug.group_id
                JOIN users u ON ug.user_id = u.id
                LEFT JOIN health_metrics hm_current ON u.id = hm_current.user_id 
                    AND hm_current.date = :selected_date
                LEFT JOIN questionnaire_data qd_current ON u.id = qd_current.user_id 
                    AND qd_current.date = :selected_date
                LEFT JOIN health_metrics hm7 ON u.id = hm7.user_id 
                    AND hm7.date BETWEEN :past_7_start AND :selected_date
                LEFT JOIN health_metrics hm30 ON u.id = hm30.user_id 
                    AND hm30.date BETWEEN :past_30_start AND :selected_date
                LEFT JOIN questionnaire_data qd7 ON u.id = qd7.user_id 
                    AND qd7.date BETWEEN :past_7_start AND :selected_date
                LEFT JOIN questionnaire_data qd30 ON u.id = qd30.user_id 
                    AND qd30.date BETWEEN :past_30_start AND :selected_date
                WHERE u.role = 'participant'
                GROUP BY g.id, g.group_name
                ORDER BY g.group_name
            )
            SELECT 
                group_id,
                group_name,
                physio_current_day_count,
                questionnaire_current_day_count,
                physio_7_day_count,
                physio_30_day_count,
                questionnaire_7_day_count,
                questionnaire_30_day_count,
                total_participants
            FROM group_summary
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {
                "selected_date": selected_date,
                "past_7_start": past_7_start,
                "past_30_start": past_30_start
            })
            
            groups_data = []
            for row in result:
                group_dict = {}
                for idx, col in enumerate(result.keys()):
                    group_dict[col] = row[idx]
                groups_data.append(group_dict)
                
            return groups_data
            
    except Exception as e:
        logger.error(f"Error getting group data summary: {e}")
        return []


def get_group_daily_data_counts(start_date, end_date):
    """
    Get daily counts of physiological and questionnaire data for all groups over a date range.
    Returns data for line plots showing trends over time.
    """
    try:
        logger.debug(f" get_group_daily_data_counts called with start_date={start_date}, end_date={end_date}")
        
        # Convert dates to datetime objects if they're strings
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        logger.debug(f" After conversion - start_date={start_date}, end_date={end_date}")
        
        # Generate date series and cross join with all groups to ensure all groups appear for all dates
        query = text("""
            WITH date_series AS (
                SELECT generate_series(
                    CAST(:start_date AS date),
                    CAST(:end_date AS date),
                    interval '1 day'
                )::date AS date
            ),
            group_dates AS (
                SELECT 
                    ds.date,
                    g.id as group_id,
                    g.group_name
                FROM date_series ds
                CROSS JOIN groups g
            )
            SELECT 
                gd.date,
                gd.group_id,
                gd.group_name,
                -- Count participants with physiological data for this date
                COUNT(DISTINCT hm.user_id) as physio_count,
                -- Count participants with questionnaire data for this date
                COUNT(DISTINCT qd.user_id) as questionnaire_count
            FROM group_dates gd
            LEFT JOIN user_groups ug ON gd.group_id = ug.group_id
            LEFT JOIN users u ON ug.user_id = u.id AND u.role = 'participant'
            LEFT JOIN health_metrics hm ON u.id = hm.user_id AND hm.date = gd.date
            LEFT JOIN questionnaire_data qd ON u.id = qd.user_id AND qd.date = gd.date
            GROUP BY gd.date, gd.group_id, gd.group_name
            ORDER BY gd.date, gd.group_name
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {
                "start_date": start_date,
                "end_date": end_date
            })
            
            daily_data = []
            for row in result:
                row_dict = {}
                for idx, col in enumerate(result.keys()):
                    row_dict[col] = row[idx]
                daily_data.append(row_dict)
            
            logger.debug(f" Returning {len(daily_data)} rows of daily data")
            if daily_data:
                logger.debug(f" Sample row: {daily_data[0]}")
                
            return daily_data
            
    except Exception as e:
        logger.error(f"Error getting group daily data counts: {e}")
        return []