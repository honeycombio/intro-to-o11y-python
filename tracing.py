import os
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
from opentelemetry.context.context import Context
import typing
from opentelemetry.propagate import set_global_textmap
from opentelemetry.semconv.resource import ResourceAttributes

from grpc import ssl_channel_credentials
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env. (automatic on glitch; this is needed locally)

# Set up tracing
service_name = os.getenv("OTEL_SERVICE_NAME", "sequence-of-numbers")
resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: service_name
})
trace.set_tracer_provider(TracerProvider(resource=resource))

apikey = os.environ.get("HONEYCOMB_API_KEY", "missing API key")
print("Sending traces to Honeycomb with apikey <" + apikey + "> to service " + service_name)

# Send the traces to Honeycomb
hnyExporter = OTLPSpanExporter(
    endpoint="api.honeycomb.io:443",
    insecure=False,
    credentials=ssl_channel_credentials(),
    headers=(
        ("x-honeycomb-team", apikey),
    )
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(hnyExporter))

# To see spans in the log, uncomment this:
# trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))


# auto-instrument outgoing requests
RequestsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())
