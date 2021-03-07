from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


def index(request):
    return HttpResponse("Hello raincloud!")


class Data(View):

    @method_decorator(csrf_exempt)
    def get(self, request, sensor_id, *args, **kwargs):
        print(f"received data from sensor id: {sensor_id}")

        body = json.loads(request.body)
        print(body['timestamp'])
        print(body['value'])

        # Write data to Timestream

        return HttpResponse(201)


class SensorList(View):

    def get(self, request, *args, **kwargs):
        body = {
            "results": [1, 2]
        }

        return HttpResponse(json.dumps(body), status=200, content_type="application/json")


class SensorDetail(View):

    def get(self, request, sensor_id, *args, **kwargs):

        if sensor_id == 1:
            body = {
                "sensor_id": 1,
                "type": "pressure",
                "units": "HPa",
                "location": "desk",
                "description": "test pressure sensor"
            }

        elif sensor_id == 2:
            body = {
                "sensor_id": 1,
                "type": "pressure",
                "units": "HPa",
                "location": "desk",
                "description": "test pressure sensor"
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