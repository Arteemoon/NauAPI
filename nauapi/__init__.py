import requests


class NauAPI(object):

    _state = {
        "week_day": {
            'Пнд': 1,
            'Втр': 2,
            'Cрд': 3,
            'Чтв': 4,
            'Птн': 5,
        },
        "call_pair": {
            1: {
                "start": "8.00",
                "end": "9.20"
            },
            2: {
                "start": "9.40",
                "end": "11.00"
            },
            3: {
                "start": "11.20",
                "end": "12.40"
            },
            4: {
                "start": "13.00",
                "end": "14.20"
            },
            5: {
                "start": "14.40",
                "end": "16.00"
            },
            6: {
                "start": "16.20",
                "end": "17.40"
            },
            7: {
                "start": "18.00",
                "end": "19.20"
            },
            8: {
                "start": "19.40",
                "end": "21.00"
            },

        }
    }

    def __init__(self):
        self.base_url = 'http://rozklad.nau.edu.ua/api/v1'

    def _reverse_url(self, url, **data):
        val = url
        for key, value in data.items():
            val = val.replace("{" + key + "}", str(value))
        return val

    def _make_request(self, endpoint, **kwargs):
        if kwargs:
            endpoint = self._reverse_url(endpoint, **kwargs)
        request = requests.get(self.base_url + endpoint)
        response = request.json()
        if response['status']:
            return response[list(response.keys())[-1]]
        return response['message']


    @property
    def departments(self):
        endpoint = '/departments'
        departments = self._state.get('departments')
        if not departments:
            departments = self._make_request(endpoint)
            self._state['departments'] = departments
        return departments

    @property
    def department_names(self):
        return [department['NAME'] for department in self.departments]

    @property
    def call_pair(self):
        return self._state['call_pair']

    @property
    def department_short_names(self):
        return [department['SHORT'] for department in self.departments]

    @property
    def department_chiefs(self):
        return [{department['SHORT']:department['CHIEF']} for department in self.departments]

    def get_department(self, department_code):
        for department in self.departments:
            if department['CODE'] == department_code:
                return department

    def get_department_groups(self, department_code):
        endpoint = '/groups/{department_code}'
        return self._make_request(endpoint, department_code=department_code)

    def get_department_group(self, department_code, group):
        groups = self.get_department_groups(department_code)
        for grp in groups:
            if grp['GRP'] == group:
                return grp

    def get_call_pair(self, pair_num):
        return self._state['call_pair'].get(pair_num)

    def get_schedules(self, department_code, course, stream, group_code, subgroup=1):
        endpoint = '/schedule/{department_code}/{course}/{stream}/{group_code}/{subgroup}'
        return self._make_request(endpoint, department_code=department_code, course=course, stream=stream, group_code=group_code, subgroup=subgroup)

    def _filter_schedules_by_week(self, schedules, week):
        return filter(lambda schedule_key: schedule_key.startswith(str(week)), schedules)

    def _filter_schedules_by_day(self, schedule_keys, day):
        return filter(lambda schedule_key: self._state["week_day"].get(schedule_key.split('.')[1]) == day, schedule_keys)

    def get_schedule(self, department_code, course, stream, group_code, subgroup, week, day, only_lecture=False):
        schedules = self.get_schedules(department_code, course, stream, group_code, subgroup)
        schedule_keys = self._filter_schedules_by_week(schedules, week)
        schedule_keys = self._filter_schedules_by_day(schedule_keys, day)
        return [schedules[schedule_key] for schedule_key in schedule_keys if schedules[schedule_key]["isLecture"] == only_lecture]

