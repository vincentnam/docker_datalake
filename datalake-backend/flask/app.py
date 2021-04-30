from flask import Flask, request
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello Modis!'

@app.route('/storage', methods= ['GET', 'POST'])
def storage(self):
    idType = request.form['idType']
    print(idType)
    data =  request.form['data']
    print(data)
    premieremeta =  request.form['premieremeta']
    print(premieremeta)
    deuxiememeta =  request.form['deuxiememeta']
    print(deuxiememeta)
    
    return 'storage'


if __name__ == '__main__':
    app.run()
