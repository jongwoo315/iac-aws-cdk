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

class S3ObjUpload(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html
        s3_obj_upload_bucket = s3.Bucket(
            self,
            id='S3ObjUploadBucket',
            bucket_name='s3-obj-upload-bucket'
        )
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_s3/Bucket.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/PolicyStatement.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/AnyPrincipal.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/StarPrincipal.html
        s3_obj_upload_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[
                    # A principal representing all AWS identities in all accounts.
                    # Some services behave differently when you specify Principal: '*' or Principal: { AWS: "*" } in their resource policy.
                    # AnyPrincipal renders to Principal: { AWS: "*" }.
                    # This is correct most of the time, 
                    # but in cases where you need the other principal, use StarPrincipal instead.
                    # iam.AnyPrincipal() 

                    # StarPrincipal renders to Principal: *.
                    # Most of the time, you should use AnyPrincipal instead.
                    iam.StarPrincipal()  
                ],
                actions=[
                    's3:PutObject',
                    's3:PutObjectAcl',
                    's3:GetObject',
                    's3:GetObjectAcl',
                    's3:DeleteObject'
                ],
                resources=[
                    'arn:aws:s3:::s3-obj-upload-bucket',
                    'arn:aws:s3:::s3-obj-upload-bucket/*'
                ]
            )
        )

        ecr.Repository(
            self,
            id='WebServiceRepo',
            repository_name=config.get('s3_obj_upload', 'ecr_repo_web_service')  # repo name은 대문자 사용 불가능
        )

        ecr.Repository(
            self,
            id='WebFrameworkRepo',
            repository_name=config.get('s3_obj_upload', 'ecr_repo_web_framework')  # repo name은 대문자 사용 불가능
        )
