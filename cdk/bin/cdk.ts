#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { InfraStack } from '../lib/infra';
import { AppStack } from '../lib/app';

const app = new cdk.App();

// バックエンド用の親スタック
class BackendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new InfraStack(this, 'InfraStack');
    new AppStack(this, 'AppStack');
  }
}

// バックエンドスタックをデプロイ
new BackendStack(app, 'BackendStack');
