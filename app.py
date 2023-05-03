#!/usr/bin/env python3
from configparser import ConfigParser
import aws_cdk as cdk
from iac_aws_cdk.secret_creation import SecretCreation
from iac_aws_cdk.ecs_task import EcsTask
from iac_aws_cdk.jw_app import JwApp
from iac_aws_cdk.pub_ec2_test import PubEc2Test
from iac_aws_cdk.s3_obj_upload import S3ObjUpload
from iac_aws_cdk.box_office_mojo import BoxOfficeMojo
from iac_aws_cdk.eb_network_stack import EbNetworkStack
from iac_aws_cdk.eb_stack import EbStack

config = ConfigParser()
config.read('config/prod.ini')

app = cdk.App()


SecretCreation(
    app,
    'SecretCreation',
    env=cdk.Environment(
        account=config.get('ecs_task', 'aws_account'),
        region=config.get('ecs_task', 'aws_region')
    )
)


EcsTask(
    app,
    'EcsTask',
    env=cdk.Environment(
        account=config.get('ecs_task', 'aws_account'),
        region=config.get('ecs_task', 'aws_region')
    )
)


JwApp(
    app,
    'JwApp',
    env=cdk.Environment(
        account=config.get('jw_app', 'aws_account'),
        region=config.get('jw_app', 'aws_region')
    )
)


PubEc2Test(
    app,
    'PubEc2Test',
    env=cdk.Environment(
        account=config.get('jw_app', 'aws_account'),
        region=config.get('jw_app', 'aws_region')
    )
)


S3ObjUpload(
    app,
    'S3ObjUpload',
    env=cdk.Environment(
        account=config.get('s3_obj_upload', 'aws_account'),
        region=config.get('s3_obj_upload', 'aws_region')
    )
)

BoxOfficeMojo(
    app,
    'BoxOfficeMojo',
    env=cdk.Environment(
        account=config.get('box_office_mojo', 'aws_account'),
        region=config.get('box_office_mojo', 'aws_region')
    )
)

# Important Environment settings. Note: Make sure to check most recent valid versions of `beanstalk_stack`
# https://awscli.amazonaws.com/v2/documentation/api/latest/reference/elasticbeanstalk/list-available-solution-stacks.html
props = {
            'namespace':'MyNamespace',
            'vpc_name':'vpc-myvpc',
            'instance_name':'rds-webserver',
            'instance_type':'t2.small',
            'wan_ip': '1.1.1.1',
            'beanstalk_stack': '64bit Amazon Linux 2 v3.4.1 running Python 3.8',
            'eb_name':'myEbApp',
            'db_master_username': 'tutorial_user',
            'db_subnet_group_name': 'sgp-rds-db',
            'db_name': 'EBDb',
            'db_instance_identifier':'tutorial-db-instance',
            'db_instance_engine':'MYSQL'
        }


eb_network_stack_result = EbNetworkStack(
    app,
    'EbNetworkStack',
    props,
    env=cdk.Environment(
        account=config.get('eb_network_stack', 'aws_account'),
        region=config.get('eb_network_stack', 'aws_region')
    )
)


eb_stack_result = EbStack(
    app,
    'EbStack',
    eb_network_stack_result.output_props,
    env=cdk.Environment(
        account=config.get('eb_stack', 'aws_account'),
        region=config.get('eb_stack', 'aws_region')
    )
)
eb_stack_result.add_dependency(eb_network_stack_result)

app.synth()
