from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/giuliano")
def giuliano():
  return "Ciao Giuliano!"

if __name__ == "__main__":
  l = [1, 2, 3, 4, 5]
  a, b, *c = l
  
  print(a, b, c)
  
  app.run()
