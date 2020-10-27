from django.shortcuts import render, redirect
from django.db.models import F
from django.contrib.auth.decorators import user_passes_test

from datetime import datetime

from .models import ScheduledDate


# TODO: Create pyautogui test for the multiple request at the same time

# TODO: Implement the logic of 5 doctors on the morning, and 3 on the afternoon


def index(request):
    return render(request, 'api/index.html')


def api_index(request):
    return render(request, 'api/api.html')


def check_admin(user):
    return user.is_superuser


@user_passes_test(check_admin)
def api_detail(request):
    return render(request, 'api/detail.html', {'scheduled_meetings': ScheduledDate.objects.all()})


def handle_request_post_data_to_api_schedule(request):
    # Standard checks
    if ('date' and 'hours' and 'minutes' and 'name') not in request.POST:
        return redirect('schedule_error', error_code=1)

    """
    Date is a html input, whose type is 'date'
    It looks like this: 10-25-2020 (mm-dd-yyyy)

    Day: 25
    Month: 10
    Year: 2020


    Hours: 18
    Minutes: 59
    """  # Stupid time-variables ...
    date = request.POST['date']
    [day, month, year] = [date.split('-')[-i] for i in range(1, 4)]
    hours = request.POST['hours']
    minutes = request.POST['minutes']

    # name of the company for organization's sake
    company_name = request.POST['name']

    return {
        'day': day,
        'month': month,
        'year': year,
        'hours': hours,
        'minutes': minutes,
        'company_name': company_name,
    }


def api_schedule(request):

    post_request = handle_request_post_data_to_api_schedule(request)

    """ Check 1: Checking if the meeting was scheduled to a saturday or to a sunday.
    
    The month variable is not 0 index ( html values ... ).
    Because of that, datetime_string has to consider the month value, and subtract 1.
    ( months[int(post_request["month"]) - 1] ).
    
    All those datetime variables were created in order to check the day of the date object passed through the html.
    datetime.weekday requires a datetime object and returns an integer.
    This integer is the 0-index-based value of the days of the week.
    So, monday = 0, tuesday = 1, ... saturday = 5, sunday = 6.
    Then, it simply checks if the datetime_weekday variable is greater than 5, if so, it's either a saturday or sunday.
    """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # months[int(month) - 1] -> months is 0-based while month is not
    datetime_string = f'{months[int(post_request["month"]) - 1]} {post_request["day"]} {post_request["year"]} ' \
                      f'{post_request["hours"]}:{post_request["minutes"]}'

    # passing all the variables to a datetime object
    datetime_object = datetime.strptime(datetime_string, '%b %d %Y %H:%M')

    # get the week day of the datetime_object date
    # monday = 0, tuesday = 1, ..., saturday = 5, sunday = 6
    datetime_weekday = datetime.weekday(datetime_object)
    if datetime_weekday >= 5:
        return redirect('schedule_error', error_code=2)

    """ Check 2: Check if the meeting was scheduled to the past
    
    It takes usage of the datetime_object previously created to check 1.
    
    Datetime objects in general are 'weird'. The newer it is, the greater it is.
    So, a datetime object for like '2006 Jun 12 13:30PM' is smaller than '2012 Jun 12 13:30PM'.
    With that in mind, we check for the current date (datetime.now()) and compare with the datetime object.
    If the current date is greater than the datetime_object, the datetime_object is in the past.
    """
    current_date = datetime.now()

    if current_date > datetime_object:  # AKA, if it's in the past
        return redirect('schedule_error', error_code=3)

    """ Check 3: Check if day and hour is available, and then check if there's no over than 5 meetings scheduled.
    
    Retrieve all the scheduled_dates from the database and compare with the datetime_object.
    If a match on the day is found, it checks for the time, if a match occurs, then they're scheduled for the same time.
    
    sanitized_scheduled_date[0] is the same as the date, it looks like this:
        * sanitized_scheduled_date[0]:  '2020-10-29'
        * sanitized_datetime_object[0]: '2020-10-29'
    
    sanitized_scheduled_date[1] is the same as the time, it looks like this:
        * sanitized_scheduled_date[1]:  '12:00:00'
        * sanitized_datetime_object[1]: '12:00:00'
        
    **Note**: Since the user can only schedule a meeting on either 0 or 30 minutes, it's really not necessary to check
    for hours and only after that, minutes. That's why the time itself is compared, and not hours, and only then, 
    minutes.
    """
    scheduled_dates = ScheduledDate.objects.all()

    sanitized_datetime_object = str(datetime_object).split(' ')

    for scheduled_date in scheduled_dates:
        sanitized_scheduled_date = str(scheduled_date).split(' ')

        """
        * Check if the 5 doctors logic is correct
        
        Both sanitized dates have the same format: year-month-day.
        Check for the day, if they're on the same day, check for the time.
        If they're on the same time, check for the database_object.count value.
        
        The business rule here is:
            * This 'count' value cannot be greater than 5.
        
        If the value is smaller than or equals 4, we can add one more schedule.
        
        **Note**: The whole code should be race-condition-issue free.
        **Note**: The database_object is the value retrieved from the database itself. 
            What does that mean ?
            It means that the select_for_update() freezes the database for the transaction.
                * Again, it should be race-condition-issue free. 
            We then increase the count value ( number of meetings scheduled )
            Push the name of the business name ( Company Name ) to the array of names in the database.
            We then save it, closing the 'freeze' time.
        """
        # if they're on the same day
        if sanitized_scheduled_date[0] == sanitized_datetime_object[0]:
            sanitized_scheduled_time = str(scheduled_date).split(' ')[1].split('+')[0]

            # if they're on the same time ( both hours, and minutes )
            if sanitized_scheduled_time == sanitized_datetime_object[1]:

                # database_object is the object value retrieved through the database itself
                database_object = ScheduledDate.objects.select_for_update().get(date=datetime_object)

                # if less than 5 people already scheduled to this time
                if database_object.count < 5:

                    # schedule normally
                    database_object.count = F('count') + 1
                    database_object.name_set.create(name=post_request['company_name'])
                    database_object.save()

                else:
                    return redirect('schedule_error', error_code=4)

    """
    No more need to keep track of current time zone.
    Since USE_TZ is now set to False, and the timezone code
    is correct ('America/Sao_Paulo'), there isn't need to
    make the datetime object aware.
    
    The code will remain commented for knowledge sake. 
    """
    # current_timezone = timezone.get_current_timezone()
    # print(f'Current timezone: {current_timezone}')
    # timezone_aware_date = current_timezone.localize(datetime_object)
    # print(f'Timezone aware date: {timezone_aware_date}')

    """ Check 5: Check if meeting was scheduled, if it wasn't, scheduled it.
    
    This code is quite tricky, let's go slow
    
    ! ScheduledDate.objects.get_or_create(date=datetime_object)[1]:
        * It checks if the object (datetime_object) is already in the database
        * The function returns a tuple with the following values: 
            (date object, boolean value)
            
            1. Date object
                It returns the value of the date, if it was already in the database, it returns the value from the
                database. If the value wasn't in the database already ( brand new object ), it returns the brand new
                object. In this case, the brand new object is the variable 'datetime_object'
            2. Boolean value
                The boolean value is just the confirmation if the value was on the database or not:
                
                False: The value is already in the database ( in this case it doesn't enter the if statement and just
                goes to the return redirect(...) statement.
                
                True: The value wasn't on the database ( it is a brand new object ), if so, the object lacks a name.
                So, inside the if statement, we add a name to it.
                
                **Note**: Notice how we're using the select_for_update() function. Because we're of course, avoiding
                race-condition situations.    
    """
    if ScheduledDate.objects.get_or_create(date=datetime_object)[1]:
        database_object = ScheduledDate.objects.select_for_update().get(date=datetime_object)
        database_object.name_set.create(name=post_request['company_name'])

    return redirect(
        'schedule_success',
        post_request['day'],
        post_request['month'],
        post_request['year'],
        post_request['hours'],
        post_request['minutes'],
        post_request['company_name'],
    )


def api_error(request, error_code):
    return render(request, 'api/schedule_error.html', {'error_code': error_code})


def api_success(request, day, month, year, hours, minutes, company_name):
    return render(request, 'api/schedule_success.html', {
        'day': day,
        'month': month,
        'year': year,
        'hours': hours,
        'minutes': minutes,
        'company_name': company_name
    })
