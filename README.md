# Discord-ninshou-URL-bot
### ⚠️このBotは1サーバー 1Botを想定してコーディングされています⚠️
## Botのセットアップ
#### Pythonを使える環境と脳みそ、Botアカウントの作成ができることが前提に話が進みます
以下のPythonモジュールをインストールしておきます
- discord.py
- requests
- flask
  
Discord Developer Portalにアクセス  
https://discord.com/developers/applications  
名前はなんでもいいのでアプリケーションを作成しましょう  
作成したらまずOAuth2のGeneralからCLIENT IDとCLIENT SECRETを控えておきます  
![1](image/1.png)  
そして、その下にあるRedirectsにFlaskサーバーを建てる場所を入力します  
Flaskサーバーのデフォルトポートは5000なのでポートには5000と記入しておきます  
![2](image/2.png)  
そうしたら1つ下にあるURL Generatorから認証に必要なURLを作成しましょう  
このURLも後で使うので控えておきます
![3](image/3.png)  
