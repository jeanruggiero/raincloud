import os
import datetime
import boto3
import math
from botocore.config import Config


class TimestreamClient:

    DB_NAME = 'raincloud-archive'
    TABLE_NAME = 'sensor-data'

    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=os.environ.get('TIMESTREAM_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('TIMESTREAM_SECRET_ACCESS_KEY')
        )

        self.client = session.client('timestream-query', region_name="us-west-2")
        self.paginator = self.client.get_paginator('query')

    def read(self, sensor_id, record_count=10, sample_rate=None, start_time=None, end_time=None):
        """

        :param sensor_id: the unique id of the sensor to query
        :param record_count: number of records to return
        :param sample_rate: sample rate in samples per second
        :param start_time: the start time of the returned data
        :param end_time: the end time of the returned data
        :return: the recorded data from the requested sensor
        :raises ValueError: if sample_rate of zero is provided
        """

        if sample_rate == 0:
            raise ValueError("Sample rate must be nonzero.")

        if sample_rate:
            time_interval = math.floor(1 / sample_rate)
            ago_start = f'AND time > ago({(datetime.datetime.now() - start_time).seconds}s)' if start_time else ''
            ago_end = f'AND time < ago({(datetime.datetime.now() - end_time).seconds}s)' if end_time else ''

            query = f"""
                SELECT BIN(time, {time_interval}s) AS binned_timestamp, ROUND(AVG(measure_value::double), 
                    2) AS avg_value
                FROM "raincloud-archive"."sensor-data"
                WHERE measure_name = '{sensor_id}'
                    {ago_start}
                    {ago_end}
                GROUP BY BIN(time, {time_interval}s)
                ORDER BY binned_timestamp DESC
                {f'LIMIT {record_count}' if record_count else ''}
            """

        else:
            query = f"""
                SELECT * 
                FROM "raincloud-archive"."sensor-data" 
                WHERE measure_name = '{sensor_id}' 
                ORDER BY time DESC 
                LIMIT {record_count}
            """

        return self.run_query(query)

    def run_query(self, query):
        pages = self.paginator.paginate(QueryString=query)

        # TODO: handle pagination better to send consistent response to client
        return [self._parse_query_result(page) for page in pages]

    def _parse_query_result(self, query_result):

        data_col, time_col = self._parse_column_info(query_result)

        return {
            'Data': [self._parse_row(data_col, time_col, row) for row in query_result['Rows']]
        }

    @staticmethod
    def _parse_column_info(query_result):

        column_info = query_result['ColumnInfo']

        data_col = None
        time_col = None

        # Find the columns containing the measured data and the timestamp
        for j, column in enumerate(column_info):
            if column['Name'] == 'measure_value::double' or column['Name'] == 'avg_value':
                data_col = j
            elif column['Name'] == 'time' or column['Name'] == 'binned_timestamp':
                time_col = j

        if data_col is None or time_col is None:
            raise ValueError("Could not find data and/or time columns.")

        return data_col, time_col

    @staticmethod
    def _parse_row(data_col, time_col, row):
        """Return a dict containing the value and timestamp for the row"""

        data = row['Data']

        return {
            'Value': data[data_col]['ScalarValue'],
            'Timestamp': data[time_col]['ScalarValue']
        }
