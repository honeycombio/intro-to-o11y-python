from flask import Flask, request
import requests

from opentelemetry import trace
from opentelemetry.ext import http_requests
from opentelemetry.sdk.trace import TracerSource
from opentelemetry.sdk.trace.export import (
  SimpleExportSpanProcessor,
  ConsoleSpanExporter,
)
from opentelemetry.ext.lightstep import LightStepSpanExporter
from opentelemetry.ext.jaeger import JaegerSpanExporter
from opentelemetry.ext.flask import instrument_app

trace.set_preferred_tracer_source_implementation(lambda T: TracerSource())

lsExporter = LightStepSpanExporter(
  name="otel-workshop",
  token="du/9Cv+uCOMKItR/vpHm+J/K8E81ZVPq3pTSGbZ4qR228DibbQ4WIYkhP4mF/F/E4BscrddJnev+pT+lyhY="
)

exporter = JaegerSpanExporter(
  service_name="otel-workshop",
  agent_host_name="35.237.84.236",
  agent_port=6831,
)
trace.tracer_source().add_span_processor(SimpleExportSpanProcessor(lsExporter))

tracer = trace.get_tracer(__name__)

http_requests.enable(trace.tracer_source())

app = Flask(__name__)
instrument_app(app)


@app.route("/")
def root():
  return "Click [Tools] > [Logs] to see spans!"


@app.route("/fib")
@app.route("/fibInternal")
def fibHandler():
  value = int(request.args.get('i'))
  returnValue = 0
  if value < 2:
    returnValue = 1
  else:
    minusOnePayload = {'i': value - 1}
    minusTwoPayload = {'i': value - 2 }
    with tracer.start_as_current_span("get_minus_one"):
      respOne = requests.get('http://127.0.0.1:5000/fibInternal', minusOnePayload)
    with tracer.start_as_current_span("get_minus_two"):
      respTwo = requests.get('http://127.0.0.1:5000/fibInternal', minusTwoPayload)
    returnValue = int(respOne.content) + int(respTwo.content)
  return str(returnValue)

if __name__ == "__main__":
  app.run(debug=True)
