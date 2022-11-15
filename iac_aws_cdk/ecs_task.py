from configparser import ConfigParser
import json
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_events as events,
    aws_events_targets as event_targets
)
from constructs import Construct

config = ConfigParser()
config.read('config/prod.ini')

class EcsTask(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        default_vpc = ec2.Vpc.from_lookup(
            self,
            id='DefaultVpc',
            vpc_id=config.get('ecs_task', 'vpc_id')
        )

        deployment_example_cluster = ecs.Cluster(
            self,
            id='DeploymentExampleCluster',
            cluster_name='DeploymentExampleCluster',
            vpc=default_vpc,
            enable_fargate_capacity_providers=True
        )

        # my_repo = ecr.Repository.from_repository_name(
        #     self,
        #     id='MyRepo',
        #     repository_name=config.get('ecs_task', 'ecr_repo')  # repo name은 대문자 사용 불가능
        # )
        my_repo = ecr.Repository(
            self,
            id='MyRepo',
            repository_name=config.get('ecs_task', 'ecr_repo')  # repo name은 대문자 사용 불가능
        )

        # https://github.com/aws/aws-cdk/issues/18926
        # https://docs.aws.amazon.com/mediaconnect/latest/ug/iam-policy-examples-asm-secrets.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/Role.html
        secrets_access_role = iam.Role(
            self,
            id='SecretsAccessRole',
            role_name='SecretsAccessRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            # 여러 개인 경우에는 iam.compositeprincipal()사용
            # assumed_by=iam.CompositePrincipal(
            #     'ecs-tasks.amazonaws.com',
            #     'ecs-tasks.amazonaws.com',
            #     'ecs-tasks.amazonaws.com',
            # )
        )
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/Policy.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/PolicyStatement.html
        secrets_access_policy = iam.Policy(
            self,
            id='SecretsAccessPolicy',
            policy_name='SecretsAccessPolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        'secretsmanager:GetResourcePolicy',
                        'secretsmanager:GetSecretValue',
                        'secretsmanager:DescribeSecret',
                        'secretsmanager:ListSecretVersionIds',
                        'secretsmanager:ListSecrets'
                    ],
                    resources=[
                        '*'
                    ]
                )
            ]
        )
        secrets_access_role.attach_inline_policy(policy=secrets_access_policy)
        
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_iam/ManagedPolicy.html
        # aws console에서 arn주소를 잘 확인해야 한다. 어떤 건 service-role/ 이 붙어 있는 것들도 있다. (job-function/도 있고, 없는 것도 있고)
        secrets_access_role.add_managed_policy(
            policy=iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess')
        )
        secrets_access_role.add_managed_policy(
            policy=iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonECSTaskExecutionRolePolicy')
        )

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_ecs/ContainerImage.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_ecs/FargateTaskDefinition.html
        deployment_example_task = ecs.FargateTaskDefinition(
            self,
            id='DeploymentExampleTask',
            family='DeploymentExampleTask',
            memory_limit_mib=512,
            cpu=256,
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX
            ),
            # console화면: task definition > builder > task role
            task_role=secrets_access_role,  # secrets manager value에 접근 (console화면: iam > roles > {roles name} > permissions)
        )
        deployment_example_task.add_container(
            id='DeploymentExampleContainer',
            image=ecs.ContainerImage.from_ecr_repository(
                repository=my_repo,
                tag='latest'
            ),
            logging=ecs.LogDriver.aws_logs(stream_prefix='ecs'),
            # https://stackoverflow.com/questions/67715261/aws-cdk-possible-to-access-individual-json-value-within-a-secrets-manager-se
            # task definition이 아니라 container에 직접 추가하는 방법도 있다.
            # secrets=''
        )

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

        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events/Rule.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events/Schedule.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.core/Duration.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events_targets/EcsTask.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events_targets/LambdaFunction.html
        # https://github.com/aws-samples/aws-cdk-examples/blob/master/typescript/lambda-cron/index.ts
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_events_targets/ContainerOverride.html
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_ec2/SecurityGroup.html
        custom_pub_subnet1 = ec2.Subnet.from_subnet_attributes(
            self,
            id='CustomPubSubnet1',
            subnet_id=config.get('ecs_task', 'vpc_subnet'),  # EcsLbTest2PrivateStack/CustomVpc1/CustomPubSubnet1
            availability_zone=config.get('ecs_task', 'aws_region'),
        )

        my_schedule = events.Rule(
            self,
            id='MySchedule',
            rule_name='MySchedule',
            # schedule=events.Schedule.cron(day='', hour='', minute='', month='', week_day='', year=''),
            # schedule=events.Schedule.rate(duration=Duration.hours(2))
            # schedule=events.Schedule.expression('0/3 * ? * * *'),  # cron()까지 str에 넣어야 한다.
            schedule=events.Schedule.expression('cron(0/2 * ? * * *)'),
            targets=[
                event_targets.EcsTask(
                    cluster=deployment_example_cluster,
                    task_definition=deployment_example_task,
                    subnet_selection=ec2.SubnetSelection(
                        subnets=[
                            custom_pub_subnet1
                        ]
                    ),
                    security_groups=[
                        ec2.SecurityGroup.from_security_group_id(
                            self,
                            id='MySecurityGroup',
                            security_group_id=config.get('ecs_task', 'sg_id')
                        )
                    ],
                    container_overrides=[
                        event_targets.ContainerOverride(
                            container_name=config.get('ecs_task', 'ecs_container'),
                            command=[
                                "python",
                                "-m",
                                "src.run"
                            ]
                        )
                    ],
                    # role=secrets_access_role,
                    task_count=1,
                    
                ),
                # event_targets.LambdaFunction(
                #     handler='',
                #     retry_attempts=''
                # )
            ]
        )