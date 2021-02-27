from flask import Flask,render_template,request,redirect,url_for,abort
from PIL import Image,ImageOps
import numpy as np
import tempfile
import os,glob,io
import math
import base64

app = Flask(__name__)

#文字列をバイト単位で数値に変換
def width_c(f,width):
    data = []                   #画像配列
    stock = []                  #ストック配列
    width_count = 0             #横幅のカウント
    element_count = 0           #要素数
    element_calc = 0            #要素計算
    num_of_array_elements = width   #配列要素数,幅の大きさ

    while True:
        byte_data = f.read(1)   #1byteずつ読み込み

        if len(byte_data) == 0: #if Endpoint fileなら
            element_count = len(stock)  #要素数にストック数を入れる
            element_calc = num_of_array_elements-element_count #幅に合う配列の残りを計算
            for width_count in range(element_calc):   #配列の残りを0パディング
                stock.append(0)             #ストックに入れる
            data.append(stock)              #ストックをデータに挿入
            break

        int_data = ord(byte_data)   #byte列からint列へ
        stock.append(int_data)
        width_count = width_count+1   #幅のカウント

        if width_count == num_of_array_elements:             #幅のカウント == 幅の大きさ
            data.append(stock) 
            stock = []         #ストックの初期化
            width_count = 0    #幅カウントの初期化
        
    f.close
    return data  #配列を返す

#ファイルサイズにしたがって画像化字の横幅を決定し、数値データに変換
def imaging(text,size):

    if 10000 > size:
        width = 32
        data = width_c(text, width)
    elif 10000 <= size < 30000:
        width = 64
        data = width_c(text, width)
    elif 30000 <= size < 60000:
        width = 128
        data = width_c(text, width)
    elif 60000 <= size < 100000:
        width = 256
        data = width_c(text, width)
    elif 100000 <= size < 200000:
        width = 384
        data = width_c(text, width)
    elif 200000 <= size < 500000:
        width = 512
        data = width_c(text, width)
    elif 500000 <= size < 1000000:
        width = 768
        data = width_c(text, width)
    elif 100000 <= size:
        width = 1024
        data = width_c(text, width)

    data = np.array(data,dtype=np.uint8)    #np配列に変換
    image = Image.fromarray(data,mode='L')  #dateをPILのImage型に変換

    return image    #Image型を変換

@app.route("/",methods=["GET","POST"])
def upload_file():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        #アップロードされたファイルを一時保存
        f = request.files["file"]
        filepath = tempfile.mkdtemp()+"\\"+f.filename  #tempfile関数でメモリ上にPATHを作成
        f.save(filepath)
        text = open(filepath, 'r' ,encoding="utf-8_sig")#一時保存

        #画像化処理
        size = os.path.getsize(filepath)    #ファイルのサイズを取得
        img_data = imaging(text,size)
        imgpath = tempfile.mkdtemp()
        img_data.save(imgpath + f.filename +".png")  #作成した画像を一時保存

        #base64でエンコード
        buffer = io.BytesIO()
        img_data.save(buffer,format="PNG")  
        img_string = base64.b64encode(buffer.getvalue()).decode('utf-8').replace("'","")

        #HTMLへ返す
        result = "画像が出力されました。"
        return render_template("index.html", filepath=filepath,result=result, img_data=img_string)


if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=False)