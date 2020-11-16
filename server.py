
from opentelemetry import (
  trace
)
from opentelemetry.ext.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
  SimpleExportSpanProcessor,
  BatchExportSpanProcessor,
  ConsoleSpanExporter,
)
from opentelemetry.ext.lightstep import LightStepSpanExporter
from opentelemetry.ext.honeycomb import HoneycombSpanExporter
from opentelemetry.ext.jaeger import JaegerSpanExporter
from opentelemetry.ext.flask import FlaskInstrumentor

FlaskInstrumentor().instrument()

from flask import Flask, request
import requests
import os
import sys

trace.set_tracer_provider(TracerProvider())

serviceName = os.environ['PROJECT_NAME']

lsExporter = LightStepSpanExporter(
  name=serviceName,
  token=os.environ['LS_KEY']
)

hnyExporter = HoneycombSpanExporter(
	service_name=serviceName,
	writekey=os.environ['HNY_KEY'],
	dataset="opentelemetry",
)

exporter = JaegerSpanExporter(
  service_name=serviceName,
  agent_host_name=os.environ['JAEGER_HOST'],
  agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(BatchExportSpanProcessor(exporter))
trace.get_tracer_provider().add_span_processor(SimpleExportSpanProcessor(ConsoleSpanExporter()))
# trace.get_tracer_provider().add_span_processor(BatchExportSpanProcessor(lsExporter))
trace.get_tracer_provider().add_span_processor(BatchExportSpanProcessor(hnyExporter))

tracer = trace.get_tracer(__name__)

RequestsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())

app = Flask(__name__)


@app.route("/")
def root():
  sys.stdout.write('\n')
  return "Click [Tools] > [Logs] to see spans!"


@app.route("/fib")
@app.route("/fibInternal")
def fibHandler():
  value = int(request.args.get('i'))
  current_span = tracer.get_current_span()
  current_span.set_attribute("request", value)
  returnValue = 0
  if value == 1 or value == 0:
    returnValue = 0
  elif value == 2:
    returnValue = 1
  else:
    minusOnePayload = {'i': value - 1}
    minusTwoPayload = {'i': value - 2}
    with tracer.start_as_current_span("get_minus_one") as span:
      span.set_attribute("payloadValue", value-1)
      respOne = requests.get('http://127.0.0.1:5000/fibInternal', minusOnePayload)
    with tracer.start_as_current_span("get_minus_two") as span:
      span.set_attribute("payloadValue", value-2)
      respTwo = requests.get('http://127.0.0.1:5000/fibInternal', minusTwoPayload)
    returnValue = int(respOne.content) + int(respTwo.content)
  sys.stdout.write('\n')
  return str(returnValue)

if __name__ == "__main__":
  app.run(debug=True)
