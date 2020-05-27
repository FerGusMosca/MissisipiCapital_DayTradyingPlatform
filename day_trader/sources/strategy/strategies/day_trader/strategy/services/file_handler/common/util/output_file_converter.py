class OutputFileConverter:

    def __init__(self):
        pass

    @staticmethod
    def CreateOuputRows(backtestDtoArr):

        dictTimes = {}
        dictDates = {}
        arrRows = []

        for dto in backtestDtoArr:
            dictTimes[dto.Time] = dto.Time

            if dto.Date not in dictDates:
                dictDates[dto.Date] = []

            dictDates[dto.Date].append(dto)

        rowTimes = "Date,"
        for time in dictTimes.keys():
            rowTimes += time.strftime("%H:%M") +","

        arrRows.append(rowTimes)

        for date in dictDates.keys():
            row = date.strftime("%m/%d/%y") + ","

            for dto in dictDates[date]:
                row += str( dto.Shares ) + ","

            arrRows.append(row)

        return arrRows