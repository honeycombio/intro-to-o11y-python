from opentelemetry import (
  trace
)
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
  SimpleSpanProcessor,
  BatchSpanProcessor,
  ConsoleSpanExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from grpc import ssl_channel_credentials

FlaskInstrumentor().instrument()

from flask import Flask, request
import requests
import os
import sys

resource = Resource(attributes={
    "service_name": "my-service"
})

trace.set_tracer_provider(TracerProvider(resource=resource))

# lsExporter = OTLPSpanExporter(
# 	endpoint="ingest.lightstep.com:443",
# 	insecure=False,
# 	credentials=ssl_channel_credentials(),
# 	headers=(
# 		("lightstep-access-token", os.environ.get("LS_KEY"))
# ))

hnyExporter = OTLPSpanExporter(
	endpoint="api.honeycomb.io:443",
	insecure=False,
	credentials=ssl_channel_credentials(),
	headers=(
		("x-honeycomb-team", os.environ.get("HNY_KEY")),
		("x-honeycomb-dataset", "opentelemetry")
	)
)

# exporter = JaegerExporter(
#   agent_host_name=os.environ['JAEGER_HOST'],
#   agent_port=6831,
# )

trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
# trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(exporter))
# trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(lsExporter))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(hnyExporter))

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
  # TODO fix missing root span b/c of w3c header
  # python equivalent of: othttp.WithSpanOptions(trace.WithNewRoot())
  # or: othttp.NewHandler(othttp.WithPublicEndpoint())
  # from workshop template slide 64
  current_span = trace.get_current_span()
  current_span.set_attribute("parameter", value)
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
