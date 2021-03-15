from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .timestream import TimestreamClient


def index(request):
    return HttpResponse("Hello raincloud!")


class Data(View):

    @csrf_exempt
    def get(self, request, sensor_id, *args, **kwargs):
        timestream_client = TimestreamClient()
        data = timestream_client.read(sensor_id, record_count=request.GET.get('n', None))

        return HttpResponse(json.dumps(data), status=200, content_type="application/json")


class Status(View):
    @csrf_exempt
    def get(self, request, *args, **kwargs):
        sensors = [
            {
                "sensor_id": 1,
                "type": "humidity",
                "units": "%",
                "location": "indoor garden",
                "description": "relative humidity"
            },
            {
                "sensor_id": 2,
                "type": "temperature",
                "units": "deg C",
                "location": "indoor garden",
                "description": "ambient temperature"
            },
            {
                "sensor_id": 3,
                "type": "soil_moisture",
                "units": "",
                "location": "indoor garden basil 1 inch cell",
                "description": "soil moisture basil ch0"
            }
        ]

        timestream_client = TimestreamClient()

        for sensor in sensors:
            data = timestream_client.read(sensor['sensor_id'], record_count=1)[0]['Data'][0]
            sensor['value'] = data['Value']
            sensor['timestamp'] = data['Timestamp']

        return HttpResponse(json.dumps({"status": sensors}), status=200, content_type="application/json")


class SensorList(View):

    def get(self, request, *args, **kwargs):
        body = {
            "results": [1, 2, 3]
        }

        return HttpResponse(json.dumps(body), status=200, content_type="application/json")


class SensorDetail(View):

    def get(self, request, sensor_id, *args, **kwargs):

        if sensor_id == 1:
            body = {
                "sensor_id": 1,
                "type": "humidity",
                "units": "%",
                "location": "indoor garden",
                "description": "relative humidity"
            }

        elif sensor_id == 2:
            body = {
                "sensor_id": 2,
                "type": "temperature",
                "units": "deg C",
                "location": "indoor garden",
                "description": "ambient temperature"
            }

        elif sensor_id == 3:
            body = {
                "sensor_id": 3,
                "type": "soil_moisture",
                "units": "",
                "location": "indoor garden basil 1 inch cell",
                "description": "soil moisture basil ch0"
            }
        else:
            return HttpResponseNotFound()

        return HttpResponse(json.dumps(body), status=200, content_type="application/json")



"""
get sensor?query_params
Default - return all 
query_params:
type=pressure
units
location

https://stackoverflow.com/questions/150505/capturing-url-parameters-in-request-get


get sensor/<sensor_id>


post /data/<sensor_id>/
    body:
        {
            timestamps: [
                time,
                time,
                time
            ],
            values: [
                value,
                value, 
                value
            ]
        }

get /data/<sensor_id>?query_params
    default: return last 12 hours of data
    query_params:
        start_time
        end_time
        sample_rate


Sensor:
- type (pressure, temperature, etc)
- units
- description
- sample rate
- measid
- location

"""