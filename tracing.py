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
from opentelemetry.propagators import textmap
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)
from opentelemetry.propagate import set_global_textmap

from grpc import ssl_channel_credentials
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env. (automatic on glitch; this is needed locally)

# Set up tracing
resource = Resource(attributes={
    "service_name": os.getenv("SERVICE_NAME", "fib-microsvc")
})
trace.set_tracer_provider(TracerProvider(resource=resource))

apikey = os.environ.get("HONEYCOMB_API_KEY", "missing API key")
dataset = os.getenv("HONEYCOMB_DATASET", "otel-python")
print("Sending traces to Honeycomb with apikey <" + apikey + "> to dataset " + dataset)

# Send the traces to Honeycomb
hnyExporter = OTLPSpanExporter(
    endpoint="api.honeycomb.io:443",
    insecure=False,
    credentials=ssl_channel_credentials(),
    headers=(
        ("x-honeycomb-team", apikey),
        ("x-honeycomb-dataset", dataset)
    )
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(hnyExporter))

# To see spans in the log, uncomment this:
# trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))


# auto-instrument outgoing requests
RequestsInstrumentor().instrument(tracer_provider=trace.get_tracer_provider())

# This part is only for Glitch - because we want to break out of THEIR traces
class DistrustRemoteTraceContext(TraceContextTextMapPropagator):
  def extract(
      self,
      carrier: textmap.CarrierT,
      context: typing.Optional[Context] = None,
      getter: textmap.Getter = textmap.default_getter,
  ) -> Context:
    if context is None:
      context = Context()
    xff = getter.get(carrier, "x-forwarded-for")
    if not xff:
      return super().extract(carrier, context, getter=getter)
    return context

set_global_textmap(DistrustRemoteTraceContext())
