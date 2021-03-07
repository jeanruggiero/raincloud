from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import json


def index(request):
    return HttpResponse("Hello raincloud!")


class Data(View):

    def post(self, request, sensor_id, *args, **kwargs):
        print(f"received data from sensor id: {sensor_id}")
        body = json.loads(request.body)
        print(body)


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