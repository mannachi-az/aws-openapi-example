from aws_cdk import (
    Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
    aws_lambda as _lambda,
    aws_iam as _iam, 
    Tags,
    CfnOutput,
    DockerImage,
    BundlingOptions,
    aws_logs as logs,
    aws_apigateway as apigateway,
    Fn,
    IResolvable
)

from constructs import Construct
from os import (
    path
)

class NcbCdkTemplateStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        lambda_execution_policy = _iam.ManagedPolicy(
            self,
            "ModelExecutionPolicy",
            document=_iam.PolicyDocument(
                statements=[
                    _iam.PolicyStatement(
                        actions=[
                            "lambda:GetAccountSettings"
                        ],
                        effect=_iam.Effect.ALLOW,
                        resources=[
                            "*",
                        ],
                    )
                ]
            ),
        )


        #Create role
        lambda_role = _iam.Role(scope=self, id='cdk-lambda-role',
            assumed_by =_iam.ServicePrincipal('lambda.amazonaws.com'),
            role_name='cdk-lambda-role',
            managed_policies=[
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaVPCAccessExecutionRole'),
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'),
                lambda_execution_policy
            ])

        cdk_lambda = _lambda.Function(
            self, 'cdk-r4p-lambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name='cdk-r4p-lambda',
            description='Lambda function deployed using AWS CDK Python',
            #code=_lambda.Code.from_asset('./lambda/sample'),
            code=_lambda.Code.from_asset("./lambda/sample",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                    command=["bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"
                    ]
                )
            ),
            handler='lambda_function.lambda_handler',
            role=lambda_role,
            environment={
                'Env': 'dev'
            },
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.THREE_MONTHS
        )
        cdk_lambda.node.default_child.override_logical_id("APILambda");
        
        # Adding Tags to Lambda

        Tags.of(cdk_lambda).add("Owner", "Sample Owner")

        # Transform Open API Yaml and deploy to API gateway
        open_api_asset = s3_assets.Asset(self, "open-api-asset", path=path.join("./apispec", "openapi.yaml"))
        transformMap = {'Location':open_api_asset.s3_object_url}
        data = Fn.transform("AWS::Include", transformMap);
        api = apigateway.SpecRestApi(self, "widgets-api",
            api_definition=apigateway.AssetApiDefinition.from_inline(data)
        )

        # Give access to api gateway to call lambda function

        cdk_lambda.add_permission(
            "lambdaPermission",
            action="lambda:InvokeFunction",
            principal=_iam.ServicePrincipal("apigateway.amazonaws.com"),
            source_arn=api.arn_for_execute_api()
        )

        #Output of created resource
        CfnOutput(scope=self, id='cdk-output',
                       value=cdk_lambda.function_name)
