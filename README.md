# Discord-Backup-Bot
ソースコードの2次配布、販売はお控えください

## Botについて
ソースを公開していますがコーディング、ホスティングの過程を省きたい場合は僕がすでにデプロイしているものを使ってみてください  
### サーバー -> https://discord.gg/aSyaAK7Ktm  
↓バックアップ / メンバーブーストBot↓  
https://discord.com/api/oauth2/authorize?client_id=1096727990655778876&permissions=8&scope=bot  
BotのHTMLは [Ame-x](https://github.com/EdamAme-x) さんが作成してくれました！  
しかも無償で。Thankyou very much!!
## OAuth2トークンの有効期限について
### メンバーブーストに使っているトークンですが、1週間で期限が切れます
対策としてはリフレッシュトークンを使ってアクセストークンを再発行することです  
EAGMを使えば簡単に短く収まります
```py
from EAGM import EAGM

token="Discord Bot Token"
cid="Client ID"
cse="Client Secret"
ruri="Redirect URI"

eagm=EAGM(bot_token=token,client_id=cid,client_secret=cse,redirect_uri=ruri,proxy=None)

print(eagm.refresh("refresh_token")) #<- リフレッシュ作業はこの1行だけ！
```
返り値はこんな感じです
```
{'token_type': 'Bearer', 'access_token': 't7KOqezBkvQbBCiKyRG3aW4GfwJD4Q', 'expires_in': 604800,
 'refresh_token': 'tnKw3UtwqrernhImzDkEEP4eJwkiQh', 'scope': 'guilds.join identify'}
```
この1連の作業をバックアップBotのソースコードに記載&データベース更新でリフレッシュ作業終了です！

## Botのセットアップ
### Pythonを使える環境と脳みそ、ある程度のファイル操作とネットワーク知識、Botアカウントの作成と編集ができることが前提に話が進みます

以下のPythonモジュールをインストールしておきます
- discord.py
- requests
- flask
- EAGM
  
Discord Developer Portalにアクセス  
https://discord.com/developers/applications  
名前はなんでもいいのでアプリケーションを作成しましょう  
作成したらまずOAuth2のGeneralからCLIENT IDとCLIENT SECRETを控えておきます  
![1](image/1.png)  
その下にあるRedirectsにFlaskサーバーを建てる場所を入力します  
Flaskサーバーのデフォルトポートは5000なのでポートには5000と記入しておきます  
##### この時末尾に"/"を入れるのを忘れないで！
![2](image/2.png)  
そうしたら1つ下にあるURL GeneratorのSCOPESで"identify"と"guilds.join"を選択、  
SELECT REDIRECT URLにはさっき入力したアドレスを選択して認証に必要なURLを作成しましょう  
このURLも後で使うので控えておきます  
![3](image/3.png)  
もちろんBotなのでBotのトークンもコピーしておいてください  
  
これでDeveloper Portalから必要になる情報は以上です  
いったんDeveloper Portalを離れてローカル環境で編集します
## ローカルでの作業
リポジトリからv6をダウンロードして使用します  
このBotはjson形式でユーザー情報を保存するので好きなところに好きな名前でjsonファイルを作ってください  
この時作ったjsonファイルには {} とだけ記載しておいて、jsonとしてちゃんと機能するようにしておいてください  
- 僕は"userdata.json"という名前で作成しました
  
そうしたらエディターかメモ帳かでv6path.pyを開きます  
- 僕はVisual Studio Codeを使いました

#### v6path.py
```py
BOTTOKEN = "MTE5NjA5NDkyMDQwMjkzO~~~~~"
CLIENT_ID = "119609492~~~~~~~"
CLIENT_SECRET = "neyNtIZTOgzbnxyRX~~~~~~~~~~"
REDIRECT_URI = "http://GlobalIP:5000/"

usadata_path = "C:/Users/Taka/Downloads/v5/userdata.json"
serverdata_folder_path = "C:/Users/Taka/Downloads/v5/server/"
authurl = "[作ったURLをここに](https://discord.com/api/oauth2/authorize?~~~~~scope=identify+guilds.join)"
```
これの入力が終わったらninV6.pyを実行してBotを起動できます！  
### サーバーに接続できない、500が返される
- ちゃんとポートが開放されているかチェックしてください
- 自分のグローバルIPに自分のグローバルIPから接続することはできません、ローカルで動作チェックをするならローカルIPを使ってください  
### /callや/request1をしてもユーザーの追加に失敗する
- Botが参加していないサーバーには参加させることができません
- 追加しようとしたあいてがアプリケーション認証を切っていると追加できません  
  対策もありません、もういっかい認証してもらうしかないです
- 上記以外でアクセストークンが失効している  
  例えばトークンをリフレッシュしない場合、1週間で期限切れになって使えなくなります
### ロール付与に失敗する
- Botにそのロールを付与する権限があるか確認してください  
  また、付与できる状態かどうかも確認してください
## Botコマンド
- button  
  登録リンクとロール付与のボタンを表示します  
  タイトルと説明を省くとテンプレートの文章を送ります
- call  
  jsonに保存されたユーザー全員を追加します、誤爆には充分気をつけてください
- request1  
  指定したIDのユーザーを追加します  
- check  
  指定したユーザーIDの情報が登録されているか確認します
- datacheck  
  jsonに何人の情報が登録されているか確認します
- delkey  
  指定したユーザーIDの登録情報を削除します
### 余談
jsonの特徴を知っている方ならお気づきだと思いますが非同期で/callを使うと2重でjsonが開かれ、dumpも2回行われます  
( 非同期で/callを使っているとして ) もし最初の/callでjsonが変更されても2重で開かれている方は開いた時点のデータを参照するため不都合が起きます ( しかもそのデータをdumpする )  
json以外のデータベースに変更するのが解法でしょう、実際に僕がホスティングしてるBotはSQLiteを使用しています.....  
  
補足  
データベースは上記の通りjsonだし、callは非同期になってるもののEAGMのリクエストは非同期じゃない  
このBotは完璧な状態ではありません...  
## コンタクト  
Discord サーバー / https://discord.gg/aSyaAK7Ktm  
Discord ユーザー名 / .taka.  
