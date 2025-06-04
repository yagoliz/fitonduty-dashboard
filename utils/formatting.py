from datetime import datetime, date

def parse_and_format_date(date_string: str) -> date:
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",  
        "%Y-%m-%dT%H:%M:%S",     
        "%Y-%m-%d"               
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            return dt.date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_string}")