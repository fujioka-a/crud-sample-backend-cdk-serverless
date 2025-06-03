import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';

export interface GlobalStackProps extends cdk.StackProps {
    readonly originUrl: string;
}

export class GlobalStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: GlobalStackProps) {
        // CloudFront は us-east-1 でデプロイするため env を指定
        super(scope, id, {
            env: { region: 'us-east-1' },
            ...props,
        });

        // originUrl は Lambda Function URL を想定
        const originUrlParsed = new URL(props.originUrl);
        const originDomain = originUrlParsed.host;
        // CloudFront用に、CloudFront に付与するカスタムヘッダー値
        const customSecret = "MY_CLOUDFRONT_SECRET";

        const distribution = new cloudfront.Distribution(this, 'WebDistribution', {
            defaultBehavior: {
                origin: new origins.HttpOrigin(originDomain, {
                    customHeaders: {
                        "x-custom-secret": customSecret,
                    },
                }),
                viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            },
        });

        new cdk.CfnOutput(this, 'CloudFrontDomain', {
            description: "CloudFront Distribution Domain Name",
            value: distribution.distributionDomainName,
        });
    }
}
