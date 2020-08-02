from sources.strategy.strategies.day_trader.strategy.services.file_handler.common.util.input_file_converter import *
from sources.strategy.strategies.day_trader.strategy.services.file_handler.common.util.output_file_converter import *
from sources.framework.common.logger.message_type import *
import shutil
import os
import threading
import csv
import traceback

class FileHandler:

    def __init__(self):
        pass

    @staticmethod
    def MoveFile( input, output):
        """ Move csv file, from input to output.

        Args:
            input (String): Current csv file path.
            output (String): Destination csv file path.

        """
        shutil.move(input, output)

    @staticmethod
    def WriteOutputSharesFile(logger,outputPath,symbol,backtestDtoArr):
        csvRows = OutputFileConverter.CreateSharesRows(backtestDtoArr)

        fileName = outputPath + symbol + "_shares_" + datetime.datetime.now().strftime("%d-%b-%Y_%H_%M_%S_%f") + ".csv"

        with open(fileName, mode='w') as output_file:
            for row in csvRows:
                output_file.write(row + '\n')

    @staticmethod
    def WriteOutputProfitsFile(logger, outputPath, symbol, backtestDtoArr):
        csvRows = OutputFileConverter.CreateProfitsRows(backtestDtoArr)

        fileName = outputPath + symbol + "_profits_" + datetime.datetime.now().strftime("%d-%b-%Y_%H_%M_%S_%f") + ".csv"

        with open(fileName, mode='w') as output_file:
            for row in csvRows:
                output_file.write(row + '\n')

    @staticmethod
    def WriteOutputFile(logger,outputPath,symbol,backtestDtoArr):

        FileHandler.WriteOutputSharesFile(logger,outputPath,symbol,backtestDtoArr)

        FileHandler.WriteOutputProfitsFile(logger, outputPath, symbol, backtestDtoArr)


    @staticmethod
    def FetchInputFile(logger, inputPath, processedPath,failedPath):

        while True:
            try:
                for r, d, f in os.walk(inputPath):
                    for file in f:
                        if '.csv' in file:
                            logger.DoLog("Found CSV file {}. Extracting simulated market data".format(file), MessageType.INFO)
                            structToTest = InputFileConverter.ExtractMarketDataStructure(logger,inputPath+file)

                            FileHandler.MoveFile(inputPath + file,processedPath + file)
                            logger.DoLog("File Handler Module : Moving file {} to {}".format(inputPath + file, processedPath + file),MessageType.INFO)

                            threading.Thread(target=logger.OnStrategyToTest, args=(structToTest,)).start()


                time.sleep(3)
            except Exception as e:
                traceback.print_exc()
                logger.DoLog("Critical error fetching for input files @FileHandlerModule.FetchInputFileThread: " + str(e), MessageType.ERROR)
                FileHandler.MoveFile(inputPath + file, failedPath + file)
