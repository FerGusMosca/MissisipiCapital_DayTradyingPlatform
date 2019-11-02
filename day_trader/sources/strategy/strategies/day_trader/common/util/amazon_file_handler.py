import boto3
from sources.framework.common.logger.message_type import *
import os
import time
import shutil
from datetime import date


class AmazonFileHandler:
    def __init__(self, pInvoker, pConfiguration):
        self.Invoker = pInvoker
        self.Configuration = pConfiguration
        self.client = None

    def MoveFile(self, input, output):
        """ Move csv file, from input to output.

        Args:
            input (String): Current csv file path.
            output (String): Destination csv file path.

        """
        self.Invoker.DoLog("Moving file {} to {}".format(input, output), MessageType.INFO)
        # os.rename(input, output)
        shutil.move(input, output)

    def initialize_client(self):
        """

        """
        aws_id = self.Configuration.aws_id
        aws_secret = self.Configuration.aws_secret

        self.client = boto3.client('s3', aws_access_key_id=aws_id,
                                   aws_secret_access_key=aws_secret)

    def DownloadFile(self):
        """

        """

        today = date.today()
        current_day = today.strftime("%Y-%m-%d")
        bucket_name = self.Configuration.bucket_name
        file_path = self.Configuration.FilePath
        file_extension = self.Configuration.file_extension
        object_key = current_day + file_extension
        file_name = file_path + object_key

        try:
            self.Invoker.DoLog("Trying to download {} from: {}".format(object_key, bucket_name),
                               MessageType.INFO)

            self.client.download_file(bucket_name, object_key, file_name)

        except Exception as e:
            self.Invoker.DoLog("Error downloading CSV file: {} from: {}; {}".format(object_key, bucket_name, e),
                               MessageType.ERROR)
            return False
        return True

    def FetchFile(self):
        """

        """
        try:

            self.initialize_client()
            if self.DownloadFile():

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
