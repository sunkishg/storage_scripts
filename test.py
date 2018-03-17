import datetime, calendar, time

def get_timestamp(day_name):
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today = datetime.datetime.today()
    targetday = weekdays.index(day_name.capitalize())
    thisday = today.weekday()
    deltatotarget = (thisday - targetday) % 7
    if deltatotarget == 0:
        deltatotarget = 7
    lastfriday = today - datetime.timedelta(days=deltatotarget)
    myday = lastfriday.strftime("%Y,%m,%d,%w,%j")
    print(myday)
    myday = myday.split(",")
    myday.append(time.localtime(time.time())[-1])
    am_time_tuple = (int(myday[0]), int(myday[1]), int(myday[2]), 5, 26, 0, int(int(myday[3]) - 1), int(myday[4]), int(myday[-1]))
    pm_time_tuple = (int(myday[0]), int(myday[1]), int(myday[2]), 18, 0, 0, int(int(myday[3]) - 1), int(myday[4]), int(myday[-1]))
    am_timestamp = int(time.mktime(am_time_tuple) * 1000)
    pm_timestamp = int(time.mktime(pm_time_tuple) * 1000)
    return (am_timestamp, pm_timestamp)

x = get_timestamp("Friday")
print(x)
