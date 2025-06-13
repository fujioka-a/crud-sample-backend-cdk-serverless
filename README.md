# crud-sample-backend-cdk-serverless

## 概要

このプロジェクトは、AWS CDK を使用して構築されたサーバーレスアプリケーションのバックエンドプロジェクトです。

### 主な特徴
1. **バックエンドフレームワーク**:
   - Python の FastAPI を使用して API を構築しています。
   - FastAPI アプリケーションは `src/main.py` に定義され、ルーターは `src/routers` ディレクトリに分割されています。

2. **AWS サーバーレスアーキテクチャ**:
   - AWS Lambda を使用して FastAPI アプリケーションをホストしています。
   - Lambda 関数は Lambda Web Adapterを使用して FastAPI アプリケーションを実行します。
     - 参考: https://tmokmss.hatenablog.com/entry/serverless-fullstack-webapp-architecture-2025?_gl=1*1duj7cu*_gcl_au*MzM3MTE1MjU2LjE3NDQxMDcyOTM.

3. **認証**:
   - AWS Cognito を使用して認証を実装しています。
   - トークンのデコードや検証は `src/core/auth.py` で行われています。

4. **データストレージ**:
   - DynamoDB を使用してタスクデータを保存しています。
   - タスクのリポジトリは `src/infrastructure/repositories/task_repository.py` に実装されています。

5. **インフラストラクチャ**:
   - AWS CDK を使用してインフラストラクチャをコードで管理しています。
   - CDK スタックは `cdk/lib` ディレクトリに定義されており、Cognito、DynamoDB、CloudFront などが構築されています。

6. **依存関係管理**:
   - Python の依存関係は `poetry` を使用して管理されています（`pyproject.toml`）。
   - TypeScript の依存関係は `npm` を使用して管理されています（`cdk/package.json`）。

7. **コード品質**:
   - Python コードの静的解析には `ruff` を使用しています（`ruff.toml`）。
   - TypeScript コードの静的解析には `eslint` を使用しています。

8. **Docker サポート**:
   - Dockerfile が用意されており、コンテナ化された環境でアプリケーションを実行できます。

### ディレクトリ構成
- **`src`**: アプリケーションのソースコード。
  - `routers/`: FastAPI のルーター(プレゼンテーション層)
  - `domains/`: ドメイン層
    - `models/`: Pydantic を使用したドメインモデル・スキーマ。
    - `interfaces/`: リポジトリインターフェース。
    - `services/`: ビジネスロジック。
  - `infrastructure/`: リポジトリ操作のロジック。
    - `repositories/`: データベース操作の実装。
    - `db`: 仮：データベース接続やセッション管理など。
  - `core/`: 認証（Cognitoトークン検証）や設定関連のコード。
  - `di`: 依存性注入の設定。

- **`cdk`**: AWS CDK によるインフラストラクチャコード。
  - `lib/`: CDK スタックの定義。
  - `bin/`: CDK アプリケーションのエントリーポイント。

- **設定ファイル**:
  - `pyproject.toml`: Python の依存関係とプロジェクト設定。
  - `ruff.toml`: Python コードの静的解析設定。
  - `cdk/tsconfig.json`: TypeScript のコンパイル設定。
  - `.gitignore`, `.dockerignore`: 無視するファイルの設定。

### 主な機能
- ユーザー認証（Cognito を使用）
- タスク管理（CRUD 操作）
- サーバーレスアーキテクチャ（Lambda + DynamoDB）
- API のデプロイと管理（AWS CDK）

## 　今後の予定・課題
- テストの拡充
  - conftest.pyの利用
  - pytest-covの導入
- API ドキュメントの作成・充実
  - OpenAPI スキーマの生成とドキュメント化
- poetryからuvへの移行
