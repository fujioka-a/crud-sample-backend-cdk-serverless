import * as cdk from 'aws-cdk-lib';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as path from 'path';
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';

import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class InfraStack extends cdk.Stack {
    public readonly userPool: cognito.UserPool;
    public readonly userPoolClient: cognito.UserPoolClient;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // = 作成 ===============================================================================================
        // 認証系 ============================
        this.userPool = new cognito.UserPool(this, 'UserPool', {
            userPoolName: 'sample-user-pool',
            selfSignUpEnabled: true,
            signInAliases: {
                username: true,
                email: true,
            },
            autoVerify: {
                email: true,
            },
            standardAttributes: {
                email: {
                    required: true,
                    mutable: false,
                },
            },
            passwordPolicy: {
                minLength: 8,
                requireDigits: true,
                requireLowercase: true,
                requireUppercase: true,
                requireSymbols: false,
            },
            accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
            removalPolicy: cdk.RemovalPolicy.DESTROY, // 学習用など。本番ではRETAINを推奨
        });

        // ユーザープールクライアントの作成
        this.userPoolClient = new cognito.UserPoolClient(this, 'UserPoolClient', {
            userPool: this.userPool,
            generateSecret: false,
            authFlows: {
                adminUserPassword: true,
                userPassword: true,
            },
        });

        const authLambda = new lambda.Function(this, 'AuthHandler', {
            runtime: lambda.Runtime.PYTHON_3_12,
            handler: 'handler.main', // handler.py の main 関数
            code: lambda.Code.fromAsset(path.join(__dirname, '../../src/dependencies')),
            environment: {
                USER_POOL_ID: this.userPool.userPoolId,
                APP_CLIENT_ID: this.userPoolClient.userPoolClientId,
            },
        });

        // DB系 ============================
        const tasksTable = new dynamodb.Table(this, 'TasksTable', {
            partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
            billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
        });

        // テーブル名を環境変数として Lambda に渡す
        authLambda.addEnvironment('TASKS_TABLE_NAME', tasksTable.tableName);

        // Lambda に DynamoDB へのアクセス権限を付与
        tasksTable.grantReadWriteData(authLambda);

        // = 出力 ===============================================================================================
        new cdk.CfnOutput(this, 'UserPoolId', {
            value: this.userPool.userPoolId,
        });

        new cdk.CfnOutput(this, 'UserPoolClientId', {
            value: this.userPoolClient.userPoolClientId,
        });
    }
}
