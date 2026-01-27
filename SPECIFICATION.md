# Discord Backup Bot - 仕様定義書

## プロジェクト概要

### プロジェクト名
Discord Backup Bot v8

### 目的
Discordサーバーのメンバー情報をバックアップし、必要に応じてメンバーを復元できるシステムを提供する。

### 開発者
.taka.

### バージョン
v8 (2024)

---

## システム構成

### アーキテクチャ
- **フロントエンド**: Flask Webサーバー（HTML/CSS）
- **バックエンド**: Python (discord.py + Flask)
- **データストレージ**: JSONファイル（本番環境ではSQLite推奨）
- **認証**: Discord OAuth2

### 技術スタック
- Python 3.x
- discord.py - Discordボットフレームワーク
- Flask - Webフレームワーク
- EAGM - OAuth2トークン管理ライブラリ
- ExoClick - 広告統合

---

## 主要機能

### 1. OAuth2認証システム
**機能**: Discordユーザーの安全な認証とトークン管理

**フロー**:
1. ユーザーが認証リンクをクリック
2. Discord OAuth2認証画面へリダイレクト
3. ユーザーが権限を承認
4. コールバックURLでトークンを取得
5. ユーザー情報とトークンをJSONに保存

**使用スコープ**:
- `identify` - ユーザー情報の取得
- `guilds.join` - サーバーへの参加権限

### 2. メンバーバックアップ
**機能**: 認証したユーザーの情報を保存

**データ構造**:
```json
{
  "user_id": "access_token"
}
```

**保存場所**:
- `data/usadata.json` - 全ユーザーのアクセストークン
- `data/serverdata/{server_id}.json` - サーバー別のユーザー情報

### 3. メンバー復元
**機能**: 保存されたユーザーをサーバーに追加

**実装コマンド**:
- `/call` - 全ユーザーを追加
- `/request1` - 特定ユーザーを追加

**APIエンドポイント**:
- `PUT /guilds/{guild_id}/members/{user_id}`

**レスポンスコード**:
- 201: メンバー追加成功
- 204: 既に参加済み
- 400: サーバー参加上限到達
- 403: トークン失効
- 404: ユーザーアカウント削除済み
- 429: レートリミット

### 4. 自動ロール付与
**機能**: 認証時に指定されたロールを自動付与

**実装**:
- OAuth2コールバック時にロールAPI呼び出し
- エラーハンドリングと詳細なエラーメッセージ

### 5. Webインターフェース
**機能**: ユーザーフレンドリーなWeb UI

**ページ構成**:
- `/` - ランディングページ
- `/setup` - セットアップガイド
- `/faq` - よくある質問
- `/pricing` - 料金プラン

**広告統合**:
- ExoClick広告スクリプト
- 認証ページとランディングページに配置

---

## Botコマンド仕様

### `/button`
**説明**: 認証ボタンとロール付与設定を表示

**パラメータ**:
- `ロール` (必須): 付与するロール
- `タイトル` (任意): 表示タイトル（デフォルト: "こんにちは！"）
- `説明` (任意): 説明文（デフォルト: "リンクボタンから登録して認証完了"）

**権限**: 管理者のみ

**動作**:
1. サーバーIDとロールIDを保存
2. 認証URLを生成（stateパラメータにサーバーID）
3. Embedメッセージとボタンを送信

### `/call`
**説明**: 登録されたユーザーをサーバーに一括追加

**パラメータ**:
- `data_server_id` (任意): サーバーID（省略時は現在のサーバー、"all"で全ユーザー）

**権限**: 管理者のみ

**動作**:
1. 対象ユーザーリストを読み込み
2. 各ユーザーに対してAPI呼び出し
3. 結果を集計して報告
4. 失効トークンを削除

**統計情報**:
- added: 追加成功
- already_joined: 既に参加済み
- invalid_token: トークン失効
- rate_limited: レートリミット発生
- max_guilds_or_bad_request: サーバー参加上限
- unknown_error: 不明なエラー

### `/check`
**説明**: ユーザーIDから登録情報を検索

**パラメータ**:
- `ユーザーid` (必須): 検索するユーザーID

**権限**: 管理者のみ

**出力**: ユーザーのアクセストークン

### `/request1`
**説明**: 特定のユーザーを1人追加

**パラメータ**:
- `ユーザーid` (必須): 追加するユーザーID

**権限**: 管理者のみ

**動作**: 指定されたユーザーのトークンを使用してメンバー追加API呼び出し

### `/delkey`
**説明**: ユーザーの登録情報を削除

**パラメータ**:
- `ユーザーid` (必須): 削除するユーザーID

**権限**: 管理者のみ

**動作**: usadata.jsonから該当ユーザーのエントリを削除

### `/datacheck`
**説明**: 登録されているユーザー数を確認

**権限**: 管理者のみ

**出力**: 総登録ユーザー数

---

## データ構造

### usadata.json
```json
{
  "123456789012345678": "access_token_string_1",
  "234567890123456789": "access_token_string_2"
}
```

### serverdata/{server_id}.json
```json
{
  "role": "role_id_string",
  "user_id_1": "0",
  "user_id_2": "1"
}
```

---

## API仕様

### Discord OAuth2
**エンドポイント**: `https://discord.com/oauth2/authorize`

**パラメータ**:
- `client_id`: アプリケーションのクライアントID
- `response_type`: "code"
- `redirect_uri`: コールバックURL
- `scope`: "identify guilds.join"
- `state`: サーバーID（16進数エンコード）

### トークン取得
**エンドポイント**: `https://discord.com/api/oauth2/token`

**メソッド**: POST

**ボディ**:
```json
{
  "client_id": "CLIENT_ID",
  "client_secret": "CLIENT_SECRET",
  "grant_type": "authorization_code",
  "code": "AUTHORIZATION_CODE",
  "redirect_uri": "REDIRECT_URI"
}
```

### ユーザー情報取得
**エンドポイント**: `https://discord.com/api/users/@me`

**メソッド**: GET

**ヘッダー**: `Authorization: Bearer ACCESS_TOKEN`

### メンバー追加
**エンドポイント**: `https://discord.com/api/guilds/{guild_id}/members/{user_id}`

**メソッド**: PUT

**ヘッダー**: `Authorization: Bot BOT_TOKEN`

**ボディ**:
```json
{
  "access_token": "USER_ACCESS_TOKEN"
}
```

### ロール付与
**エンドポイント**: `https://discord.com/api/guilds/{guild_id}/members/{user_id}/roles/{role_id}`

**メソッド**: PUT

**ヘッダー**: `Authorization: Bot BOT_TOKEN`

---

## セキュリティ

### トークン管理
- アクセストークン: 7日間有効
- リフレッシュトークン: 長期保存可能
- トークンはJSONファイルに暗号化せずに保存（本番環境では暗号化推奨）

### 権限管理
- すべての管理コマンドは管理者権限が必要
- DMでのコマンド実行は禁止
- Botトークンは環境変数またはv8path.pyで管理

### データ保護
- JSONファイルはローカルストレージに保存
- 本番環境ではSQLiteやPostgreSQLへの移行を推奨
- 定期的なバックアップが必要

---

## エラーハンドリング

### OAuth2認証エラー
- スコープ不正: "400: 無効なスコープ"
- サーバー情報なし: "サーバー情報が見つかりません"

### ロール付与エラー
- 権限不足: "Botがロールを付与できる状態か確認してください"
- ロール階層: "Botのロールが付与したいロールの1つ上に配置されているか確認"

### メンバー追加エラー
- トークン失効: 403エラー → トークンを削除
- サーバー参加上限: 400エラー
- レートリミット: 429エラー → リトライ推奨

---

## パフォーマンス

### レートリミット対策
- メンバー追加時に1秒の遅延を実装
- Discord APIのレートリミット遵守

### スケーラビリティ
- JSONベースのストレージは小規模用途向け
- 大規模展開にはデータベース必須
- 非同期処理によるパフォーマンス最適化

---

## デプロイメント

### 必要環境
- Python 3.7以上
- ポート5000が開放されている環境
- インターネット接続

### 環境変数（v8path.py）
```python
BOTTOKEN = "Bot token here"
CLIENT_ID = "OAuth2 Client ID"
CLIENT_SECRET = "OAuth2 Client Secret"
REDIRECT_URI = "http://your-domain:5000/"
```

### 起動方法
```bash
python ninV8.py
```

### 本番環境推奨設定
- Gunicorn/uWSGIでのプロセス管理
- Nginx/Apacheでのリバースプロキシ
- HTTPS化（Let's Encrypt推奨）
- systemdによる自動起動
- ログローテーション設定

---

## トラブルシューティング

### よくある問題

1. **500エラー**
   - ポート開放確認
   - グローバルIP → グローバルIPの接続は不可
   - ローカルテスト時はローカルIPを使用

2. **ユーザー追加失敗**
   - Botがサーバーに参加しているか確認
   - ユーザーがアプリケーション認証を有効にしているか
   - トークン有効期限（7日）確認

3. **ロール付与失敗**
   - Botの権限確認
   - ロール階層の確認（Botロールが対象ロールより上）

---

## 今後の拡張予定

### v9以降の計画
- SQLiteデータベース統合
- リフレッシュトークン自動更新
- Web管理パネル
- 詳細なログ記録
- メトリクス収集
- マルチサーバー対応強化

---

## ライセンスと制限

### 利用規約
- ソースコードの2次配布、販売禁止
- 個人利用・非営利目的での使用推奨
- 商用利用は要相談

### サポート
- コミュニティサポート: https://discord.gg/bvRv838kkd
- 開発者コンタクト: .taka. (Discord)

---

## 付録

### 参考リンク
- Discord Developer Portal: https://discord.com/developers/applications
- Discord API Documentation: https://discord.com/developers/docs
- Flask Documentation: https://flask.palletsprojects.com/

### バージョン履歴
- v1-v7: アーカイブ済み
- v8 (現行): Web UI統合、広告対応、エラーハンドリング強化

---

*このドキュメントは Discord Backup Bot v8 のリバースエンジニアリングにより作成されました。*
*最終更新: 2024*
