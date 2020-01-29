from flask import Flask, request
import requests

from opentelemetry import trace
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware
import opentelemetry.ext.http_requests
from opentelemetry.sdk.trace import TracerSource

exporter = ConsoleSpanExporter()
trace.set_preferred_tracer_source_implementation(lambda T: TracerSource())
tracer = trace.tracer_source().get_tracer(__name__)
span_processor = BatchExportSpanProcessor(exporter)
trace.tracer_source().add_span_processor(span_processor)
opentelemetry.ext.http_requests.enable(TracerSource())

app = Flask(__name__)
app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)

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
