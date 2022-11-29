from configparser import ConfigParser
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_glue as glue
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

        mojo_athena_query_result = s3.Bucket(
            self,
            id='MojoAthenaQueryResult',
            bucket_name='mojo-athena-query-result'
        )
        mojo_athena_query_result.add_to_resource_policy(
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
                    'arn:aws:s3:::mojo-athena-query-result',
                    'arn:aws:s3:::mojo-athena-query-result/*'
                ]
            )
        )

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/Role.html
        # Only IAM roles created by the AWS Glue console 
        # and have the prefix "AWSGlueServiceRole-" can be updated. (cdk로 생성해도 보이며, prefix만 명심)

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/ServicePrincipal.html
        # https://github.com/aws/aws-cdk/issues/3316
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/PolicyDocument.html
        # https://aws.amazon.com/ko/premiumsupport/knowledge-center/glue-not-writing-logs-cloudwatch/
            # not authorized to perform: logs:PutLogEvents / on resource: arn:aws:logs:ap-northeast-2:123123123123:log-group:/aws-glue/crawlers:log-stream:test 
            # User does not have access to target s3://box-office-mojo-bucket/
            # not authorized to perform: glue:GetDatabase / on resource: arn:aws:glue:ap-northeast-2:123123123123:catalog
            # not authorized to perform: glue:GetDatabase / on resource: arn:aws:glue:ap-northeast-2:123123123123:database/test_db 
            # not authorized to perform: glue:GetTable / on resource: arn:aws:glue:ap-northeast-2:123123123123:catalog 
            # not authorized to perform: glue:GetTable / on resource: arn:aws:glue:ap-northeast-2:123123123123:table/test_db/box_office_mojo_bucket 
            # not authorized to perform: glue:CreateTable / on resource: arn:aws:glue:ap-northeast-2:123123123123:catalog 
            # not authorized to perform: glue:UpdateTable / on resource: arn:aws:glue:ap-northeast-2:123123123123:catalog
            # not authorized to perform: glue:BatchGetPartition / on resource: arn:aws:glue:ap-northeast-2:123123123123:catalog
            # not authorized to perform: glue:BatchCreatePartition / on resource: arn:aws:glue:ap-northeast-2:123123123123:catalog
            # not authorized to perform: glue:GetPartition / on resource: arn:aws:glue:ap-northeast-2:531822071256:catalog
            # not authorized to perform: glue:GetConnection on resource: arn:aws:glue:ap-northeast-2:531822071256:catalog
        aws_glue_service_role_default = iam.Role(
            self,
            id='AWSGlueServiceRoleDefault',
            role_name='AWSGlueServiceRoleDefault',
            assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),  # role > trust relationships
            inline_policies={
                'AWSGlueServiceRoleDefaultPolicy': iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(  # role > permissions
                            effect=iam.Effect.ALLOW,
                            # principals=[
                            #     iam.StarPrincipal()  # StarPrincipal renders to Principal: *.
                            # ],
                            actions=[
                                'logs:CreateLogGroup',
                                'logs:CreateLogStream',
                                'logs:PutLogEvents',
                            ],
                            resources=[
                                'arn:aws:logs:*:*:log-group:/aws-glue/crawlers:log-stream:*',
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                's3:ListBucket',
                                's3:GetObject'
                            ],
                            resources=[
                                'arn:aws:s3:::*',
                                'arn:aws:s3:::*/*'
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                'glue:GetDatabase',
                                'glue:GetTable',
                                'glue:CreateTable',
                                'glue:UpdateTable',
                                'glue:BatchGetPartition',
                                'glue:BatchCreatePartition',
                                'glue:GetPartition',
                                'glue:GetConnection'
                            ],
                            resources=[
                                'arn:aws:glue:*:*:catalog',
                                'arn:aws:glue:*:*:database/*',
                                'arn:aws:glue:*:*:table/*',
                            ]
                        ),
                    ]
                ),
                # 'SomePolicy': iam.PolicyDocument(
                #     statements=[
                #         iam.PolicyStatement(
                            
                #         ),
                #         iam.PolicyStatement(
                            
                #         ),
                #     ]
                # ),
            }
            # managed_policies=''
        )

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnClassifier.html#cfnclassifier
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnClassifier.html#aws_cdk.aws_glue.CfnClassifier.CsvClassifierProperty
        glue.CfnClassifier(
            self,
            id='GlueTestClassifier',
            csv_classifier=glue.CfnClassifier.CsvClassifierProperty(
                name='GlueTestClassifier',
                delimiter=',',
                quote_symbol='"',
                contains_header='UNKNOWN',
                # allow_single_column='',
                # disable_value_trimming='',
            ),
        )

        # 아래 CfnCrawler에서 database는 string으로 넣으라는데 CfnDatabase는 필요x?
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnDatabase.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnDatabase.html#databaseinputproperty
        glue.CfnDatabase(
            self,
            id='GlueTestDatabase',
            # catalog_id='!Ref AWS::AccountId',
            catalog_id=config.get('box_office_mojo', 'aws_account'),  # 필수
            database_input=glue.CfnDatabase.DatabaseInputProperty(
                name='glue-test-database'  # Database name is required, in lowercase characters (s3 bucket name처럼 '-'사용)
            )  # 필수
        )

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnCrawler.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnCrawler.html#s3targetproperty
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_s3/Bucket.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnCrawler.html#aws_cdk.aws_glue.CfnCrawler.RecrawlPolicyProperty
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/Role.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_glue/CfnCrawler.html#scheduleproperty
        glue.CfnCrawler(
            self,
            id='GlueTestCrawler',
            name='GlueTestCrawler',
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        # connection_name='s333333',  # crawler > data source > network connection인 듯 / option -> 주석처리
                        path=f'{s3_obj_upload_bucket.s3_url_for_object()}/mojo'
                        # sample_size=123,
                        # exclusions=['result/**']
                    )
                ],
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior='CRAWL_EVERYTHING'
                # recrawl_behavior='CRAWL_NEW_FOLDERS_ONLY'
                # recrawl_behavior='CRAWL_EVENT_MODE'
            ),
            # classifier 내의 값은 string으로 넣어야 하는데 위에서 설정한 classifier의 id를 넣어도 되는지 모르겠음
            classifiers=[
                'GlueTestClassifier'
            ],
            role=aws_glue_service_role_default.role_arn,
            database_name='glue-test-database',
            # table_prefix='',
            # schema_change_policy='',

            # schedule frequency를 on demand로 하려면 주석처리
            # schedule=glue.CfnCrawler.ScheduleProperty(
            #     schedule_expression='cron(0 9 * * ? *)'
            # )
        )

# 1. s3 target connection name 역할 -> 없는듯? 주석처리해도 되나? -> network connection 부분 -> 주석처리해도 문제없음
# 1-2. s3 path는 fstring으로 추가 -> 문제없음
# 2. classifier 연결이 저렇게 가능? -> 생성됨 / 연결됨 (database연결과 비슷한 형태)
# 3. database는 그냥 string으로 입력 가능? -> 생성됨 / 연결안됨 -> CfnCrawler에 명시한 이름과 CfnDatabase input name만 맞추면 되는 듯
# 4. schedule은 주석처리하면 on demand형태가 되는가? -> o
