#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

import { InfraStack } from '../lib/infra';
import { AppStack } from '../lib/app';
import { GlobalStack } from '../lib/global'

const app = new cdk.App();

// バックエンド用の親スタック
class BackendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new InfraStack(this, 'InfraStack');
    const appStack = new AppStack(this, 'AppStack');

    new GlobalStack(app, 'GlobalStack', {
      originUrl: appStack.functionUrl,
    });
  }
}

// バックエンドスタックをデプロイ
new BackendStack(app, 'BackendStack');
