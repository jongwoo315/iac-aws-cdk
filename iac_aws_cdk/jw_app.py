"""custom(JwApp) vpc, subnet, sg 생성
nat instance 때문에 비용이 지속적으로 발생해서 사용안할 시에는 제거 -> nat instance, subnet들만 제거는 불가능
stack 자체를 제거 (cdk destroy)
"""
from configparser import ConfigParser
from aws_cdk import (
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct

config = ConfigParser()
config.read('config/prod.ini')

class JwApp(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        jw_app_vpc = ec2.Vpc(
            self,
            id='JwAppVpc',
            vpc_name='JwAppVpc',
            cidr=config.get('jw_app', 'vpc_cidr'),
            nat_gateway_provider=ec2.NatProvider.instance(
                instance_type=ec2.InstanceType('t2.nano')
            ),
            nat_gateways=1,
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='JwPub',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=20
                ),
                ec2.SubnetConfiguration(
                    name='JwPri',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=20
                )
            ]
        )

        jw_app_sg = ec2.SecurityGroup(
            self,
            id='JwAppSg',
            security_group_name='JwAppSg',
            description='sg for JwApp',
            vpc=jw_app_vpc,
            allow_all_outbound=True
        )
        jw_app_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'),
            connection=ec2.Port.all_tcp()
        )
        jw_app_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'),
            connection=ec2.Port.tcp(80)
        )
        jw_app_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'),
            connection=ec2.Port.tcp(443)
        )
