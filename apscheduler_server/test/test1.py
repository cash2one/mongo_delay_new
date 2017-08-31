from flask import Flask,request,Response
import json

app = Flask(__name__)


@app.route('/',methods=['GET','POST'])
def index():
    if request.method =='POST':
        result = 'tttt'
        message = request.get_json()#客户端提交数据是以form表单的形式提交，{'content':对应客户端上传的数据}\
        print (message)
        return Response(json.dumps(result), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='192.168.0.210', port=6688)