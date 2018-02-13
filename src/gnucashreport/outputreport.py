from gnucashreport.buildreport import BuildReport
from gnucashreport.report import Report, ReportInflation
from gnucashreport.reportset import ReportSet

builder = BuildReport(GnuCashData(filename))
reportset = builder.get_reportset_all()
output_xls = OutputXLS(reportset)
output_xls.write(filename)
output_hml = OutputHtml(reportset)
output.write(folder)

# Прочитать данные Book
# Построить ReportSet по мин и макc дате из book
# Заполнить ReportSet данными из raw_reports, Добавить margins
# Вывести ReportSet в нужном формате.

# ReportSet не нужно знать о raw_reports
# OutputReport - Тоже не нужно знать о raw_reports

raw_report = RawReport(book_file)


report_set = ReportSet()
report_set.fill_all(raw_report.dates) # Здесь нужны макс и мин даты, которые можно прочтитать только из данных ...
report_set.add_complex(year=2017)
report_set.add_inflation()

report_set.recieve_data(raw_report) # Только здесь нужны данные gcreport !

report_set = UnviersalReports(raw_report).All

report = ReportInflation()
report_set.add_report(report)

outputreportxls = OutputReportXLS(report_set)
outputreportxls.write(xls_file)

class OutputReport:

    def __init__(self, gcreport, reportset=None):
        self._gcreport = gcreport
        if reportset:
            self._reportset = reportset
        else:
            self._reportset = ReportSet()

    def fill_reportset(self, reportset):
        self._reportset = reportset

    def fill_reportset_all(self):
        pass

    def fill_reportset_complex(self, start_date, end_date):
        pass

    def fill_reportset_inflation(self, from_date, to_date, period, glevel):

        cumulative =False
        report = ReportInflation(from_date=from_date, to_date=to_date, period=period, cumulative=cumulative, glevel=glevel)
        self._reportset.add_report(report)

        cumulative = True
        report = ReportInflation(from_date=from_date, to_date=to_date, period=period, cumulative=cumulative,
                                 glevel=glevel)
        self._reportset.add_report(report)



    def write(self, filename):
        pass