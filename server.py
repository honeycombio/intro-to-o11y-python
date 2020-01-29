from flask import Flask
import requests

app = Flask(__name__)

@app.route("/")
def root():
  return "Click [Tools] > [Logs] to see spans!"

@app.route("/fib")
def fibHandler():
  value = request.args.get('i')
  returnValue = 0
  if value < 2:
    returnValue = 1
  else:
    for n in range(1, 2):
      payload = {'i': value -1}
      resp = requests.get('http://127.0.0.1:3000/fibInternal?', payload)
      returnValue = resp.content
  return returnValue

if __name__ == "__main__":
  app.run()
