import sys
import requests
from flask import render_template
from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor

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
    
    # Add a custom attribute for the index here
    
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
        
        # Put this calculation into its own span
        returnValue = int(respOne.content) + int(respTwo.content)
        
    sys.stdout.write('\n')
    return str(returnValue)

if __name__ == "__main__":
    app.run(debug=True)
