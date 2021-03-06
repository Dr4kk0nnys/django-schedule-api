from django.db.models import ObjectDoesNotExist

from datetime import datetime

from api.utils.exceptions import InvalidTokenId, InvalidPost, InvalidDate, InvalidDay, InvalidObject, InvalidTime
from api.models import ScheduledDate, User


def is_token_id_valid(token_id):
    if not User.objects.filter(token_id=token_id):
        raise InvalidTokenId()
    return True


def is_date_and_time_valid(day, month, year, hours, minutes):
    if len(day) != 2 or len(month) != 2:
        raise InvalidPost(message='Day and Month must be standardized! Read the "Data" at the official documentation.',
                          code=2)
    if len(year) != 4:
        raise InvalidPost(message='Year must be standardized! Read the "Data" at the official documentation.', code=2)

    if (int(day) < 1 or int(day) > 31) or (int(month) < 1 or int(month) > 12):
        raise InvalidPost(message='Day or Month value is incorrect! Read the "Data" at the official documentation.',
                          code=2)

    if len(hours) != 2 or len(minutes) != 2:
        raise InvalidPost(message='Hours and Minutes must be standardized! Read the "Data" at the official '
                                  'documentation.', code=2)

    if (int(hours) < 7 or int(hours) > 19) or (int(minutes) != 30 and int(minutes) != 0):
        raise InvalidPost(message='Hours and Minutes must be standardized! Read the "Data" at the official '
                                  'documentation.', code=2)

    return True


def is_meeting_date_available(datetime_object):
    """
    Check if the meeting was scheduled to a saturday or sunday.
    Check if the meeting was scheduled to the past.
    """
    
    # get the week day of the datetime_object date
    # monday = 0, tuesday = 1, ..., saturday = 5, sunday = 6
    datetime_weekday = datetime.weekday(datetime_object)

    if datetime_weekday >= 5:
        raise InvalidDay()
    

    current_date = datetime.now()

    if current_date > datetime_object:  # AKA, if it's in the past
        raise InvalidDate()

    return True


def is_meeting_scheduled_time_available(datetime_object):
    """
    Date objects from database should look like this:
    < QuerySet[] >:
        [0]: { Date, Count }
        Date should look like:
            year-month-day: 2020-10-30
        Count should look like:
            int: 1

    Date datetime should look like this:
        year-month-day: 2020-10-30
    Time datetime should look like this:
        hours:minutes:seconds: 04:20:00

    Datetime object:
        '2020-10-30 04:20:00'
    """
    date_objects_from_database = ScheduledDate.objects.all()

    date_datetime = str(datetime_object).split(' ')[0]
    time_datetime = str(datetime_object).split(' ')[1]

    for scheduled_date in date_objects_from_database:
        date = str(scheduled_date).split(' ')[0]
        time = str(scheduled_date).split(' ')[1]

        # if they're on the same day
        if date == date_datetime:

            # if they're on the same time ( both hours and minutes )
            if time == time_datetime:

                count = 3
                if time_datetime <= '11:30:00':
                    count = 5

                # if less than {count} people already scheduled to this time, schedule it normally
                if ScheduledDate.objects.select_for_update().get(date=datetime_object).count < count:
                    return True
                raise InvalidTime()

    return True


def is_datetime_already_on_the_database(datetime_object):
    try:
        ScheduledDate.objects.get(date=datetime_object)
    except ObjectDoesNotExist:
        raise InvalidObject()
    return True
