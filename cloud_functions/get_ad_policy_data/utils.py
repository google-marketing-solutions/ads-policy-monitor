from datetime import datetime

def get_current_date():
    current_date = datetime.now()
    # Format the returned date as 'YYYY-MM-DD'
    return current_date.strftime('%Y-%m-%d')