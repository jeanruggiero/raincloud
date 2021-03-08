import os
import boto3
from botocore.config import Config


class TimestreamClient:

    DB_NAME = 'raincloud-archive'
    TABLE_NAME = 'sensor-data'

    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=os.environ.get('TIMESTREAM_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('TIMESTREAM_SECRET_ACCESS_KEY')
        )

        self.client = session.client('timestream-query')
        self.paginator = self.client.get_paginator('query')

    def read(self, sensor_id, record_count=10):

        record_count = record_count if record_count else 10

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
            if column['Name'] == 'measure_value::double':
                data_col = j
            elif column['Name'] == 'time':
                time_col = j

        if not data_col or not time_col:
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
