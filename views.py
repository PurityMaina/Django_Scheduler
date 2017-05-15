# Create your views here.
import itertools
from django.template import RequestContext
from django.views.generic import CreateView, ListView, UpdateView
from lab_sessions.forms import SessionsForm
from projects.models import Project
from subjects.models import Subject
from utils.mixins import LoginRequiredMixin
from django.template.defaultfilters import register
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from lab_sessions.models import Session
from lab_sessions.models import Schedule

from calendar import HTMLCalendar
from itertools import groupby
from django.utils.safestring import mark_safe
from dateutil.relativedelta import relativedelta
from calendar import monthrange, day_name
from datetime import date as date_local, datetime, timedelta
import calendar as calendar_current

class SessionsCalendar(LoginRequiredMixin, ListView):
    model = Session
    template_name = "sessions/calendar_weekview.html"

    def get_context_data(self, **kwargs):
        context = super(SessionsCalendar, self).get_context_data(**kwargs)
        current_date = datetime.now()
        month = current_date.strftime("%B")
        context['month'] = str(month)
        context['year'] = datetime.now().year
        context['week'] = datetime.now().day
        context["day"] = 1
        default_calendar_view = 'month'
        context['calendar_view'] = default_calendar_view

        year = int(datetime.now().year)
        week = 1
        try:
            month = self.request.session['month']  # 5  # int(datetime.now().month)
            week = self.request.session['week']
            year = self.request.session['year']
            context['year'] = year
            month2 = month
            context['week'] = self.request.session['week']
            context['calendar_view'] = self.request.session['calendar_view']

            date_current = str(year) + "-" + str(month) + "-1"
            current_date = datetime.strptime(date_current, '%Y-%m-%d')
            month2 = current_date.strftime("%B")
            context['month'] = str(month2)
            context['month2'] = str(month)

        except Exception as e:
            month = datetime.now().month
            year = datetime.now().year

        num_days = monthrange(year, month)[1]
        days = [date_local(year, month, day) for day in range(1, num_days + 1)]
        week1_start = days[0]
        week1_end = days[6]
        week2_start = days[7]
        week2_end = days[13]
        week3_start = days[14]
        week3_end = days[20]
        week4_start = days[21]
        week4_end = days[27]
        week5_start = None
        week5_end = None

        try:
            week5_start = days[28]
            week5_end = days[len(days) - 1]

        except Exception as e:
            pass

        day = str(year) + '-' + str(month) + "-" + str(week)
        dt = datetime.strptime(day, '%Y-%m-%d')
        start = dt - timedelta(days=(dt.weekday()))
        start1 = start
        end = start + timedelta(days=6)
        start = start.strftime('%d/%b/%Y')
        end = end.strftime('%d/%b/%Y')

        dates = {}
        dates2 = {}

        start_date = None
        end_date = None

        day_sessions = {}
        sessions_dates = {}
        # start_date
        for day in range(1, 8):
            days = None
            date = datetime.strptime(str(start), "%d/%b/%Y")
            start = datetime.strptime(start, '%d/%b/%Y')
            modified_date = datetime.date(start) + timedelta(days=day - 1)
            days = datetime.strftime(modified_date, "%Y/%m/%d")
            start = start.date()
            dt = datetime.strptime(str(start), '%Y-%m-%d')
            start = dt - timedelta(days=dt.weekday())

            session_date = str(days.replace("/", "-"))
            days = datetime.strptime(days, '%Y/%m/%d')
            dates[day] = str(day_name[days.weekday()]) + ", " + \
                str(days.strftime("%B")) + " " + str(days.day)
            dates2[day] = str(session_date)
            if day == 1:
                start_date = str(days.day)
            if day == 7:
                end_date = str(days.day)
            start = start.strftime('%d/%b/%Y')

            # Get sessions
            sessions = Session.objects.filter(session_date=session_date).order_by("start_time")
            day_sessions[str(session_date)] = {}
            sessions_dates[day] = str(session_date)
            todays_sessions = {}

            i = 1
            for session in sessions:
                if session in day_sessions:
                    continue
                else:
                    todays_sessions[str(i)] = session
                i += 1
            day_sessions[str(session_date)] = todays_sessions
        context["days"] = dates
        context["days2"] = dates2
        context["total_sessions"] = i

        context["sessions_dates"] = sessions_dates
        context["day_sessions"] = day_sessions
        date_sessions = {}
        date_sessions[1] = day_sessions[sessions_dates[1]]
        date_sessions[2] = day_sessions[sessions_dates[2]]
        total2 = len(date_sessions[2])
        date_sessions[3] = day_sessions[sessions_dates[3]]
        date_sessions[4] = day_sessions[sessions_dates[4]]
        date_sessions[5] = day_sessions[sessions_dates[5]]
        date_sessions[6] = day_sessions[sessions_dates[6]]
        date_sessions[7] = day_sessions[sessions_dates[7]]
        context["days_sessions"] = date_sessions
        total1 = len(date_sessions[1])
        total2 = len(date_sessions[2])
        total3 = len(date_sessions[3])
        total4 = len(date_sessions[4])
        total5 = len(date_sessions[5])
        total6 = len(date_sessions[6])
        total7 = len(date_sessions[7])
        totals = [total1, total2, total3, total4, total5, total6]
        max_total = max(totals)
        context["max_total"] = range(1, (max_total + 1))
        context["max_total2"] = max_total

        context["total1"] = range(total1, max_total)  # range(1,(total1))
        context["total2"] = range(total2, max_total)  # range(1,(total2))
        context["total3"] = range(total3, max_total)  # range(1,(total3))
        context["total4"] = range(total4, max_total)  # range(1,(total4))
        context["total5"] = range(total5, max_total)  # range(1,(total5))
        context["total6"] = range(total6, max_total)  # range(1,(total6))
        context["total7"] = range(total7, max_total)  # range(1, (total7))

        context["total1_1"] = total1
        context["total2_1"] = total2
        context["total3_1"] = total3
        context["total4_1"] = total4
        context["total5_1"] = total5
        context["total6_1"] = total6
        context["total7_1"] = total7

        weeks = [
            str(week1_start.day) + "-" + str(week1_end.day),
            str(week2_start.day) + "-" + str(week2_end.day),
            str(week3_start.day) + "-" + str(week3_end.day),
            str(week4_start.day) + "-" + str(week4_end.day),
        ]
        try:
            weeks.append(str(week5_start.day) + "-" + str(week5_end.day))
        except Exception as e:
            pass

        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
                  ]

        context["weeks"] = weeks
        context["months"] = months
        years = []
        for year_current in range(int(((datetime.now() - relativedelta(years=1))).year),
                                  int((datetime.now() + relativedelta(years=2)).year)):
            years.append(year_current)
        context["years"] = years

        week = context["week"]

        month2 = context["month2"]

        if int(month2) < 10:
            month2 = "0" + str(month2)
        if int(week) < 10:
            week = "0" + str(week)
        session_date = str(context["year"]) + "-" + str(month2) + "-" + str(week)

        # sessions = Session.objects.filter(session_date=session_date).order_by("start_time")
        session_date = str(year) + "-" + str(month2) + "-" + str(week)
        start_date = str(year) + "-" + str(month2) + "-01"
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=int(num_days))

        sessions = Session.objects.filter(session_date__gte=start_date, session_date__lte=end_date).order_by(
            "start_time")

        context["sessions"] = sessions
        context["session_date"] = session_date

        return context

    @register.filter(is_safe=True)
    def increment(value):
        return int(value) + 1

    @csrf_exempt
    def get_queryset(self):
        month1 = int(self.request.GET.get("month", datetime.now().month))
        week = int(self.request.GET.get("week", "1"))
        year = int(self.request.GET.get("year", datetime.now().year))
        default_calendar_view = self.request.GET.get("calendar_view", 'month')
        self.request.session['month'] = month1
        self.request.session['week'] = week
        self.request.session['year'] = year
        self.request.session['calendar_view'] = default_calendar_view

        try:
            month1 = month1.encode("utf-8")
        except Exception as e:
            queryset = Session.objects.all().order_by("id")
        context = {}
        current_date = datetime.now()
        month = current_date.strftime("%B")
        context['month'] = str(month1)
        context['year'] = year
        context["day"] = 1

        month = month1

        num_days = monthrange(year, month1)[1]
        days = [date_local(year, month, day) for day in range(1, num_days + 1)]
        week1_start = days[0]
        week1_end = days[6]
        week2_start = days[7]
        week2_end = days[13]
        week3_start = days[14]
        week3_end = days[20]
        week4_start = days[21]
        week4_end = days[27]
        week5_start = None
        week5_end = None

        try:
            week5_start = days[28]
            week5_end = days[len(days) - 1]

        except Exception as e:
            pass

        day = str(datetime.now().year) + '-' + str(month1) + \
            '-1'
        dt = datetime.strptime(day, '%Y-%m-%d')
        start = dt + timedelta(days=dt.weekday())
        start1 = start
        end = start + timedelta(days=6)
        start = start.strftime('%d/%b/%Y')
        end = end.strftime('%d/%b/%Y')

        dates = {}
        dates2 = {}

        start_date = None
        end_date = None

        day_sessions = {}
        sessions_dates = {}
        # start_date
        for day in range(1, 8):
            days = None
            date = datetime.strptime(str(start), "%d/%b/%Y")
            start = datetime.strptime(start, '%d/%b/%Y')
            modified_date = datetime.date(start) + timedelta(days=day - 1)
            days = datetime.strftime(modified_date, "%Y/%m/%d")
            start = start.date()
            dt = datetime.strptime(str(start), '%Y-%m-%d')
            start = dt - timedelta(days=dt.weekday())

            session_date = str(days.replace("/", "-"))
            days = datetime.strptime(days, '%Y/%m/%d')

            dates[day] = str(calendar_current.day_name[days.weekday()]) + ", " + \
                str(days.strftime("%B")) + " " + str(days.day)
            dates2[day] = str(session_date)
            if day == 1:
                start_date = str(days.day)
            if day == 7:
                end_date = str(days.day)
            start = start.strftime('%d/%b/%Y')

            # Sessions
            sessions = Session.objects.filter(session_date=session_date).order_by("start_time")
            queryset.filter(session_date=session_date).order_by("start_time")

            day_sessions[str(session_date)] = {}
            # sessions_dates.append(str(session_date))
            sessions_dates[day] = str(session_date)
            todays_sessions = {}

            i = 1

            for session in sessions:
                if session in day_sessions:
                    continue
                else:
                    todays_sessions[str(i)] = session
                i += 1
            day_sessions[str(session_date)] = todays_sessions
        context["days"] = dates
        context["days2"] = dates2
        context["total_sessions"] = i

        context["sessions_dates"] = sessions_dates
        context["day_sessions"] = day_sessions
        date_sessions = {}
        date_sessions[1] = day_sessions[sessions_dates[1]]
        date_sessions[2] = day_sessions[sessions_dates[2]]
        total2 = len(date_sessions[2])
        date_sessions[3] = day_sessions[sessions_dates[3]]
        date_sessions[4] = day_sessions[sessions_dates[4]]
        date_sessions[5] = day_sessions[sessions_dates[5]]
        date_sessions[6] = day_sessions[sessions_dates[6]]
        date_sessions[7] = day_sessions[sessions_dates[7]]
        context["days_sessions"] = date_sessions
        total1 = len(date_sessions[1])
        total2 = len(date_sessions[2])
        total3 = len(date_sessions[3])
        total4 = len(date_sessions[4])
        total5 = len(date_sessions[5])
        total6 = len(date_sessions[6])
        total7 = len(date_sessions[7])
        totals = [total1, total2, total3, total4, total5, total6, total7]
        max_total = max(totals)
        context["max_total"] = range(1, (max_total + 1))

        context["total1"] = range(1, (total1))
        context["total2"] = range(1, (total2))
        context["total3"] = range(1, (total3))
        context["total3_1"] = total3 + 1
        context["total4"] = range(1, (total4))
        context["total5"] = range(1, (total5))
        context["total6"] = range(1, (total6))
        context["total7"] = range(1, (total7))

        weeks = [
            str(week1_start.day) + "-" + str(week1_end.day),
            str(week2_start.day) + "-" + str(week2_end.day),
            str(week3_start.day) + "-" + str(week3_end.day),
            str(week4_start.day) + "-" + str(week4_end.day),
        ]
        try:
            weeks.append(str(week5_start.day) + "-" + str(week5_end.day))
        except Exception as e:
            pass

        months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
                  ]
        years = []
        for year_current in range(int(((datetime.now() - relativedelta(years=1))).year), int((datetime.now() + relativedelta(years=2)).year)):
            years.append(year_current)
        context["years"] = years
        context["weeks"] = weeks
        context["months"] = months
        context["data2"] = "TEST"
        data = context

        if int(month1) < 10:
            month1 = "0" + str(month1)
        if int(week) < 10:
            week = "0" + str(week)
        session_date = str(year) + "-" + str(month1) + "-" + str(week)
        start_date = str(year) + "-" + str(month1) + "-01"
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=int(num_days))

        sessions = Session.objects.filter(
            session_date__gte=start_date, session_date__lte=end_date).order_by("start_time")
        context["sessions"] = sessions
        context["session_date"] = session_date
        context["default_calendar_view"] = default_calendar_view

        context = RequestContext(self.request)

        return render_to_response('sessions/calendar_weekview.html', data, context)


class ScheduleCalendar(HTMLCalendar):

    def __init__(self, workouts):
        super(ScheduleCalendar, self).__init__()
        self.workouts = self.group_by_day(workouts)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date_local.today() == date_local(self.year, self.month, day):
                cssclass += ' today'
            if day in self.workouts:
                cssclass += ' filled'
                body = ['<ul>']

                for workout in self.workouts[day]:
                    body.append('<li>')
                    body.append('<a href="%s">' % workout)
                    body.append('PEG-Africa')

                body.append('</a></li>')
                body.append('</ul>')
                return self.day_cell(cssclass, '%d %s' % (day, ''.join(body)))
            date_current = str(self.year) + "-" + str(self.month) + "-" + str(day)
            sessions = Session.objects.filter(session_date=date_current).count()
            if sessions == 1:
                label = "Session"
            else:
                label = "Sessions"
            url = "/sessions/calendar_weekview/?week=" + str(day) + "&month=" + str(self.month) + "&year=" + str(
                self.year)
            return self.day_cell(cssclass, "<a href=" + url + "><center><h2>" + str(
                day) + "</h2><br><h5 style='color:black;'>" + str(sessions) + " " + label + "</h5></center></a>")
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ScheduleCalendar, self).formatmonth(year, month)

    def group_by_day(self, workouts):
        field = lambda workout: workout.date_and_time.day
        return dict(
            [(day, list(items)) for day, items in groupby(workouts, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ScheduleCalendar, self).formatmonth(year, month)

    def group_by_day(self, workouts):
        field = lambda workout: workout.date_and_time.day
        return dict(
            [(day, list(items)) for day, items in groupby(workouts, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)


def calendar(request, year=None, month=None):
    """
    Show calendar of schedule for a given month of a given year.

    """
    if year == None:
        year = datetime.now().year
        month = datetime.now().month
    else:
        year = int(year)
        month = int(month)

    sessions = Schedule.objects.order_by('date_and_time').filter(
        date_and_time__year=year, date_and_time__month=month,
    )
    cal = ScheduleCalendar(sessions).formatmonth(year, month)
    # Calculate values for the calendar controls. 1-indexed (Jan = 1)
    my_previous_year = year - 1
    my_previous_month = month - 1
    my_next_month = month + 1
    my_next_year = year + 1

    if my_previous_month == 0:
        my_previous_year = year - 1
        my_previous_month = 12
        my_next_year = year + 1
        my_next_month = month + 1

    if my_next_month == 13:
        my_next_year = year + 1
        my_next_month = 1
        my_previous_year = year - 1

    return render_to_response('sessions/calender.html', {'calendar': mark_safe(cal),
                                                         'previous_month': my_previous_month,
                                                         'previous_month_name': my_previous_month,
                                                         'previous_year': my_previous_year,
                                                         'next_month': my_next_month,
                                                         'next_month_name': my_next_month,
                                                         'next_year': my_next_year,
                                                         'year': year,
                                                         'month': month,
                                                         })
