import json
import pprint
from datetime import date, timedelta

ADVANCE_DAYS = 5  # 单位：天
DURATION_of_TIMES = 7  # 单位：天
DATA_TEMPLATE = {'start_date': '',
                 'end_date': '',
                 'duration': 0}


class MenstrualDate:
    def __init__(self, year: int, month: int, day: int, cycle: int = 28):
        self._year = year
        self._month = month
        self._day = day
        self._cycle = cycle

        self._nearly_menstrual_end = None

    def __str__(self):
        start_date, end_date = self.next_menstrual()
        return ("+*- 最近的一次经期 -*+\n"
                f"| 开始于: {self.pred_menstrual()[0]} |\n"
                "+*- 预计下一次经期 -*+\n"
                f"| 开始于: {start_date} |\n"
                f"| 结束于: {end_date} |\n"
                "+--------------------+")

    @staticmethod
    def parse_to_dict(data: tuple | list[tuple]):

        def modify_template(start_date_, end_date_):
            t_ = DATA_TEMPLATE.copy()
            t_['start_date'] = str(start_date_)
            t_['end_date'] = str(end_date_)
            t_['duration'] = int((end_date_ - timedelta(start_date_.day)).day) + 1
            return t_

        if type(data) is tuple:
            start_date, end_date = data
            return modify_template(start_date, end_date)

        if type(data) is list:
            result = []
            for start_date, end_date in data:
                t = modify_template(start_date, end_date)
                result.append(t)
            return result

    def pred_menstrual(self):
        start = date(self._year, self._month, self._day)
        if not self._nearly_menstrual_end:
            end = start + timedelta(DURATION_of_TIMES - 1)
        else:
            end = self._nearly_menstrual_end

        return start, end

    def next_menstrual(self):
        start = date(self._year, self._month, self._day) + timedelta(self._cycle)
        end = start + timedelta(DURATION_of_TIMES - 1)
        return start, end

    def next_cus_times(self, times: int):
        if type(times) is not int:
            raise TypeError('The parameter types must be int')
        if not 1 <= times <= 12:
            raise ValueError('Maximum times is 12')

        if times == 1:
            return self.next_menstrual()

        dates = []
        _start_date = self.pred_menstrual()[0]
        for _ in range(times):
            _menstrual_date = MenstrualDate(_start_date.year, _start_date.month, _start_date.day, self._cycle)
            _date = _menstrual_date.next_menstrual()
            _start_date = _date[0]
            dates.append(_date)
        return dates

    def modify_for_future(self, cycle_: int = None, start_date_: tuple[int, int, int] = None):
        if cycle_:
            self._cycle = cycle_

        if start_date_:
            self._year, self._month, self._day = start_date_

    def date_to_json(self, type_: str, times: int = 1):
        if type_ == 'next':
            return json.dumps(self.parse_to_dict(self.next_cus_times(times)))

        if type_ == 'pred':
            return json.dumps(self.parse_to_dict(self.pred_menstrual()))

    @property
    def cycle(self):
        return self._cycle

    @property
    def nearly_menstrual_end(self):
        return self._nearly_menstrual_end

    @nearly_menstrual_end.setter
    def nearly_menstrual_end(self, value: tuple[int, int, int]):
        self._nearly_menstrual_end = date(*value)


if __name__ == '__main__':
    pred_date = MenstrualDate(2022, 12, 2)
    print(pred_date)
    pprint.pprint(pred_date.date_to_json('next', 3))
