import sys
import requests
from flask import render_template
from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import trace

import tracing

app = Flask(__name__)

# auto-instrument incoming requests
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/fib")
def fibHandler():
    i = int(request.args.get('index'))

    # CUSTOM ATTRIBUTE: Add a custom attribute for the index here. 2 lines to uncomment
    # current_span = trace.get_current_span()
    # current_span.set_attribute("parameter.index", i)

    returnValue = 0
    if i == 0:
        returnValue = 0
    elif i == 1:
        returnValue = 1
    else:
        minusOnePayload = {'index': i - 1}
        minusTwoPayload = {'index': i - 2}

        respOne = requests.get(
            'http://127.0.0.1:5000/fib', minusOnePayload)
        respTwo = requests.get(
            'http://127.0.0.1:5000/fib', minusTwoPayload)

    # CUSTOM SPAN: Put this calculation into its own span.
    # 3 lines to uncomment, and add some indent to the one surrounded
     #   tracer = trace.get_tracer(__name__)
     #   with tracer.start_as_current_span("calculate") as span:
        returnValue = int(respOne.content) + int(respTwo.content)
     #     span.set_attribute("result", returnValue)

    return str(returnValue)


if __name__ == "__main__":
    app.run(debug=False)
