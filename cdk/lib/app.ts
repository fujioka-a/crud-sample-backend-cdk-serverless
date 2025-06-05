import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';

export class AppStack extends cdk.Stack {
  public readonly functionUrl: string; // Lambda Function URL をエクスポート

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 定数：CloudFront が付与するカスタムヘッダーの値
    const customSecret = "MY_CLOUDFRONT_SECRET";

    // Lambda 関数 (FastAPI) をコンテナイメージから作成
    const webAdapterLambda = new lambda.DockerImageFunction(this, 'FastAPIFunction', {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../..'), {
        file: 'Dockerfile',
      }),
      memorySize: 1024,
      timeout: cdk.Duration.seconds(300),
      environment: {
        AWS_LWA_INVOKE_MODE: 'RESPONSE_STREAM',
      },
      tracing: lambda.Tracing.ACTIVE,
    });

    webAdapterLambda.addToRolePolicy(new iam.PolicyStatement({
      sid: "BedrockInvokePolicy",
      effect: iam.Effect.ALLOW,
      actions: ["bedrock:InvokeModelWithResponseStream"],
      resources: ["*"],
    }));

    const functionUrlObj = webAdapterLambda.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
    });

    // FunctionUrlConfig のオーバーライド
    const cfnFunction = webAdapterLambda.node.defaultChild as lambda.CfnFunction;
    cfnFunction.addPropertyOverride('FunctionUrlConfig.InvokeMode', 'RESPONSE_STREAM');

    // Lambda Function URL をエクスポート
    this.functionUrl = functionUrlObj.url;

    new cdk.CfnOutput(this, 'FastAPIFunctionUrl', {
      description: "Function URL for FastAPI function",
      value: this.functionUrl,
    });

    new cdk.CfnOutput(this, 'FastAPIFunction', {
      description: "FastAPI Lambda Function ARN",
      value: webAdapterLambda.functionArn,
    });
  }
}
