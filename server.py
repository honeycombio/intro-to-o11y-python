from flask import Flask
from flask import request
import requests

app = Flask(__name__)

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
  app.run()
