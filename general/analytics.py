from datetime import datetime, timedelta
from django.db import models
from commune.gen_utils import create_datetime, current_datetime, today_datetime, tomorrow_datetime
from user import models as user_models


def get_user_data_for_datetime(start=None, end=None):
    if not start:
        year = datetime.now().year
        month = datetime.now().month
        start = create_datetime(year, month, 1, 'Asia/Kolkata')
    if not end:
        end = current_datetime('Asia/Kolkata')

    print(start, end)
    datetimes = [start + timedelta(days=x) for x in range((end - start).days + 1)]
    days = []
    days_vs_users = []

    for i, k in enumerate(datetimes):
        current = datetimes[i]
        next = current + timedelta(days=1)

        days.append(current.strftime("%d/%m"))
        users_count = user_models.UserProfile.objects.filter(models.Q(created__gte=current),
                                                             models.Q(created__lt=next)).count()

        days_vs_users.append(users_count)

    return {'days': days, 'days_vs_users': days_vs_users}


def get_last_opened_info(start, end):
    if not start:
        start = today_datetime('Asia/Kolkata')
    if not end:
        end = tomorrow_datetime('Asia/Kolkata')

    count = user_models.UserProfile.objects.filter(models.Q(last_opened_at__gte=start),
                                                   models.Q(last_opened_at__lt=end)).count()
    return count
