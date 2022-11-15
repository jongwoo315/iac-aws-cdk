import json
from aws_cdk import (
    Stack,
    aws_secretsmanager as secretsmanager
)
from constructs import Construct


class SecretCreation(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_secretsmanager/Secret.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_secretsmanager/SecretStringGenerator.html
        secretsmanager.Secret(
            self,
            id='MyTestSecret',
            secret_name='MyTestSecret',
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({
                    'username': 'jw',
                    'phone': 123,
                    'nickname': 'dd'
                }),
                generate_string_key='password'
            )
        )
