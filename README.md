# Discord-Backup-Bot
ソースコードの2次配布、販売はお控えください

## Botについて
ソースを公開していますがコーディング、ホスティングの過程を省きたい場合は僕がすでにデプロイしているものを使ってみてください  
  
↓Bot置き場のサーバー招待 (よくBANされるので)↓  
https://discord.gg/XsfvtjSGJR
### サポートサーバー -> https://discord.gg/bvRv838kkd  
## OAuth2トークンの有効期限について
#### メンバーブーストに使っているトークンは1週間で期限が切れます
リフレッシュトークンを使ってアクセストークンを再発行できます  
EAGMを使えば簡単に短く収まります
```py
from EAGM import EAGM

eagm=EAGM(bot_token="token")

async def main():
  refresh = await eagm.refresh(refresh_token="access_token")

asyncio.run(main())
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
- flask[async]

```
pip install discord.py
pip install flask[async]
```
#### ↑をコピペでインストールできます
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
リポジトリからv8をダウンロードして使用します  
エディターかメモ帳かでv8path.pyを開きます  
- 僕はVisual Studio Codeを使いました

#### v8path.py
```py
BOTTOKEN = "Botのトークンをここに"
CLIENT_ID = "OAuth2のClientIDをここに"
CLIENT_SECRET = "OAuth2のClientSecretをここに"
REDIRECT_URI = "Flaskサーバーが建てられている場所(IPアドレスやドメイン)をここに"
```
これの入力が終わったらninV8.pyを実行してBotを起動できます！  
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
  jsonに保存されたユーザー全員を追加します、誤爆には気をつけてください
- request1  
  指定したIDのユーザーを追加します  
- check  
  指定したユーザーIDの情報が登録されているか確認します
- datacheck  
  jsonに何人の情報が登録されているか確認します
- delkey  
  指定したユーザーIDの登録情報を削除します
### 余談
久しぶりに手を加えました  
いまだにバージョンがファイル名に使われているのは質問されるときにバージョンがわからないって言われたことが多かったから  
ここではテキストエディターで開けないファイルを扱いたくないのでjsonだけど、2重に開いた時問題が起きるので公開するならSQLiteとかに移行する必要アリ  
## コンタクト  
Discord サーバー / https://discord.gg/g4UE3kQbmS  
Discord ユーザー名 / .taka.  
