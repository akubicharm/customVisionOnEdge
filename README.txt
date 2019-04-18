How to build:
==============================================

docker build -t <your image name> .

How to run locally:
==============================================
docker run -p 127.0.0.1:80:80 -d <your image name>

Then use your favorite tool to connect to the end points.

POST http://127.0.0.1/image with multipart/form-data using the imageData key
e.g
	curl -X POST http://127.0.0.1/image -F imageData=@some_file_name.jpg

POST http://127.0.0.1/image with application/octet-stream
e.g.
	curl -X POST http://127.0.0.1/image -H "Content-Type: application/octet-stream" --data-binary @some_file_name.jpg

POST http://127.0.0.1/url with a json body of { "url": "<test url here>" }
e.g.
    curl -X POST http://127.0.0.1/url -d '{ "url": "<test url here>" }'

For information on how to use these files to create and deploy through AzureML check out the readme.txt in the azureml directory.



# Edge Module


## Modules
### CameraCapture
Azure IoT EdgeのHostPathから画像データを読み込み、Classfiyアプリケーションを呼び出す

### Classify
受信した画像データの検証を Custom Vision で作成したモデルを利用して行い、検証結果をAzure IoT Hubに送信する


## How To Deploy with VSCode

### IoT Edge デバイス側の準備
1. コンテナからHostPathでマウントするディレクトリ( /work/data ) を作成する。


### VSCodeからのデプロイ
1. VSCodeで、CVSolution プロジェクトを開く
2. deployment.template.json 右クリックして [Build and Push IoT Edge Solusion] を実行する
3. config/deployment.json ができていいることを確認する
4. VSCodeでAzureにログインして、デプロイ対象のIoT Hubを選択する（コマンドパレットで実行）
5. デプロイ対象のIoT Edgeデバイスを右クリックして、[Create Deployment for Single Device]をクリックする
