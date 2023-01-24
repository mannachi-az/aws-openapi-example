import aws_cdk as core
import aws_cdk.assertions as assertions

from ncb_cdk_template.ncb_cdk_template_stack import NcbCdkTemplateStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ncb_cdk_template/ncb_cdk_template_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = NcbCdkTemplateStack(app, "ncb-cdk-template")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
