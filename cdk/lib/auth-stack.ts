import * as cdk from 'aws-cdk-lib';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as path from 'path';
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';


export class AuthBackendStack extends Stack {
    constructor(scope: Construct, id: string, props?: StackProps) {
        super(scope, id, props);

        const authLambda = new lambda.Function(this, 'AuthHandler', {
            runtime: lambda.Runtime.PYTHON_3_12,
            handler: 'handler.main', // handler.py の main 関数
            code: lambda.Code.fromAsset(path.join(__dirname, '../../src/auth')),
        });
    }
}

export class AuthStack extends cdk.Stack {
    public readonly userPool: cognito.UserPool;
    public readonly userPoolClient: cognito.UserPoolClient;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // ユーザープールの作成
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

        // 出力
        new cdk.CfnOutput(this, 'UserPoolId', {
            value: this.userPool.userPoolId,
        });

        new cdk.CfnOutput(this, 'UserPoolClientId', {
            value: this.userPoolClient.userPoolClientId,
        });
    }
}
