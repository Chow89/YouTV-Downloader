class ComparatorFactory:
    @staticmethod
    def factor(key):
        options = {
            'production_year': ProductionYearComparator(),
            'series_season': SeasonComparator()
        }
        return options[key]


class AbstractComparator:
    @classmethod
    def compare(cls, filterValue, recordValue):
        pass


class ProductionYearComparator(AbstractComparator):
    def compare(self, filterValue, recordValue):
        return filterValue <= recordValue


class SeasonComparator(AbstractComparator):
    def compare(self, filterValue, recordValue):
        return filterValue <= recordValue
