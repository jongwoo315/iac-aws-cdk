from configparser import ConfigParser
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ecr as ecr
)
from constructs import Construct

config = ConfigParser()
config.read('config/prod.ini')

class BoxOfficeMojo(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        s3_obj_upload_bucket = s3.Bucket(
            self,
            id='BoxOfficeMojo',
            bucket_name='box-office-mojo-bucket'
        )
        s3_obj_upload_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[
                    iam.StarPrincipal()  # StarPrincipal renders to Principal: *.
                ],
                actions=[
                    's3:PutObject',
                    's3:PutObjectAcl',
                    's3:GetObject',
                    's3:GetObjectAcl',
                    's3:DeleteObject'
                ],
                resources=[
                    'arn:aws:s3:::box-office-mojo-bucket',
                    'arn:aws:s3:::box-office-mojo-bucket/*'
                ]
            )
        )

        # ecr.Repository(
        #     self,
        #     id='WebServiceRepo',
        #     repository_name=config.get('s3_obj_upload', 'ecr_repo_web_service')  # repo name은 대문자 사용 불가능
        # )

        # ecr.Repository(
        #     self,
        #     id='WebFrameworkRepo',
        #     repository_name=config.get('s3_obj_upload', 'ecr_repo_web_framework')  # repo name은 대문자 사용 불가능
        # )
