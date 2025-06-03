#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { AuthStack } from '../lib/auth-stack';

const app = new cdk.App();

// バックエンド用の親スタック
class BackendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 子スタックとして AuthStack を追加
    new AuthStack(this, 'AuthStack');
  }
}

// バックエンドスタックをデプロイ
new BackendStack(app, 'BackendStack');
