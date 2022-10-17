import aws_cdk as core
import aws_cdk.assertions as assertions

from iac_aws_cdk.iac_aws_cdk_stack import IacAwsCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in iac_aws_cdk/iac_aws_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = IacAwsCdkStack(app, "iac-aws-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
