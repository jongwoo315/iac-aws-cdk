#!/usr/bin/env python3
from configparser import ConfigParser
import aws_cdk as cdk
from iac_aws_cdk.secret_creation import SecretCreation
from iac_aws_cdk.ecs_task import EcsTask
from iac_aws_cdk.jw_app import JwApp
from iac_aws_cdk.pub_ec2_test import PubEc2Test
from iac_aws_cdk.s3_obj_upload import S3ObjUpload
from iac_aws_cdk.box_office_mojo import BoxOfficeMojo

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
app.synth()
