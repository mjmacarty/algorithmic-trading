def get_next_exp(date):
    first_friday = 0
        
    if date.month == 12:
        year = date.year + 1    
    else:
        year = date.year
    if date.month == 12:
        month = (date.month + 1) % 12
    else:
        month = date.month + 1    
            
    next_month = calendar.monthcalendar(year, month)
    
    for week in next_month:
        for day in week:
            if day > 0 and calendar.weekday(year, month, day)  == calendar.FRIDAY:
                first_friday = day
                break
        if first_friday:
            break    
    return datetime(year, month, first_friday + 14).date()