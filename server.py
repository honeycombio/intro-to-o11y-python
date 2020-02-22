from flask import Flask, request
import requests

from opentelemetry import trace
from opentelemetry.ext import http_requests
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
  BatchExportSpanProcessor,
  ConsoleSpanExporter,
)
from opentelemetry.ext.flask import instrument_app

exporter = ConsoleSpanExporter()
trace.set_preferred_tracer_source_implementation(lambda T: TracerProvider())
tracer = trace.get_tracer(__name__)

span_processor = BatchExportSpanProcessor(exporter)
trace.tracer_provider().add_span_processor(span_processor)

http_requests.enable(trace.tracer_provider())

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
    respOne = requests.get('http://127.0.0.1:5000/fibInternal', minusOnePayload)
    returnValue += int(respOne.content)
    respTwo = requests.get('http://127.0.0.1:5000/fibInternal', minusTwoPayload)
    returnValue += int(respTwo.content)
  return str(returnValue)

if __name__ == "__main__":
  app.run(debug=True)
