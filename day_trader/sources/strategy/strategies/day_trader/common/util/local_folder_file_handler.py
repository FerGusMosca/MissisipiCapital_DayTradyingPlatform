from sources.framework.common.logger.message_type import *
import os
import time
import shutil


class LocalFolderFileHandler:
    def __init__(self, pInvoker, pConfiguration):
        self.Configuration = pConfiguration
        self.Invoker = pInvoker

    def MoveFile(self, input, output):
        """ Move csv file, from input to output.

        Args:
            input (String): Current csv file path.
            output (String): Destination csv file path.

        """
        self.Invoker.DoLog("Moving file {} to {}".format(input, output), MessageType.INFO)
        # os.rename(input, output)
        shutil.move(input, output)

    def FetchFile(self):
        """ Process current CSV file.
            Move file after finish processing

        """

        while True:
            try:

                for r, d, f in os.walk(self.Configuration.FilePath):
                    for file in f:
                        if '.csv' in file:
                            self.Invoker.DoLog("Found CSV file {}. Executing Positions".format(file), MessageType.INFO)
                            if self.Invoker.LaunchPositionsInCsv(self.Configuration.FilePath + file):
                                self.MoveFile(self.Configuration.FilePath + file,
                                               self.Configuration.ProcessedPath + file)
                            else:
                                self.MoveFile(self.Configuration.FilePath + file, self.Configuration.FailedPath + file)

                time.sleep(3)

            except Exception as e:
                self.Invoker.DoLog("Error processing CSV file at {}: {}".format(self.Configuration.FilePath, e),
                                   MessageType.ERROR)
                self.Invoker.DoLog("For security reasons, the fetch process will be terminated!",MessageType.ERROR)
                break

