class MonthlyReportDto:

    def __init__(self,
                 companyCode: str,
                 companyName: str,
                 year: int,
                 month: int,
                 monthlyRevenue: int,
                 ):
        self.companyCode = companyCode
        self.companyName = companyName
        self.year = year
        self.month = month
        self.monthlyRevenue = monthlyRevenue
        pass

    def to_dict(self):
        return {
            "companyCode": self.companyCode,
            "companyName": self.companyName,
            "year": self.year,
            "month": self.month,
            "monthlyRevenue": self.monthlyRevenue,
        }
        pass
