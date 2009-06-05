"""
An utility to navigate in dates.
"""


import datetime


class DateNavigator(object):

    def __init__(self, objects, date_field="date", state={}, 
            state_keys={"year": "year", "month": "month"},
            month_formatter=None):
        self.objects = objects
        self.month_formatter = month_formatter
        self.state = {}
        if state.has_key(state_keys["year"]):
            self.state["year"] = int(state[state_keys["year"]])
        else:
            self.state["year"] = None
        if state.has_key(state_keys["month"]):
            self.state["month"] = int(state[state_keys["month"]])
        else:
            self.state["month"] = None
        self.state_keys = state_keys
        # Index objects by date
        self.dates = {}
        for obj in objects:
            date = getattr(obj, date_field)
            # Index by year
            if self.dates.has_key(date.year):
                self.dates[date.year]["objects"].append(obj)
            else:
                self.dates[date.year] = {"objects": [obj], "months": {}}
            # Index by month
            months = self.dates[date.year]["months"]
            if months.has_key(date.month):
                months[date.month]["objects"].append(obj)
            else:
                months[date.month] = {"objects": [obj]}

    def selectors(self):
        year, month = self.state["year"], self.state["month"]
        if year:
            if month:
                return (year, self.textual_month(month))
            return (year,)
        return ()

    def date_items(self):
        """
        Return the list of date items under the current state.

        Each date item is a dictionnary: {"get": "...", "text": "..."}, with
        'get' being an http GET formated string corresponding to the item's 
        state and 'text' the date item text (e.g. "2007" for a year item).
        """
        year, month = self.state["year"], self.state["month"]
        items = []
        if year:
            if not month:
                fmt = "%s=%i&%s=%%i" % (self.state_keys["year"], year,
                        self.state_keys["month"])
                months = self.dates[year]["months"].keys()
                months.sort()
                for month in months:
                    items.append({
                            "get": fmt % month, 
                            "text": self.textual_month(month)
                        })
        else:
            fmt = "%s=%%i" % self.state_keys["year"]
            for year in self.dates:
                items.append({
                        "get": fmt % year, 
                        "text": year
                    })
        return items

    def objects(self):
        "Returns the list of objects corresponding to the current state"
        year, month = self.state["year"], self.state["month"]
        if year:
            if month:
                return self.dates[year]["months"][month]["objects"]
            return self.dates[year]["objects"]
        return self.objects

    def textual_month(self, month):
        """Transform a month to its textual representation"""
        if self.month_formatter is not None:
            return self.month_formatter(month)
        return datetime.date(year=1978, month=month, day=1).strftime("%B")
        
