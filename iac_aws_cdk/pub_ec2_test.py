from configparser import ConfigParser
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as elasticloadbalancingv2_targets
)
from constructs import Construct

config = ConfigParser()
config.read('config/prod.ini')


class PubEc2Test(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        jw_app_vpc = ec2.Vpc.from_lookup(
            self,
            id='JwAppVpc',
            vpc_id=config.get('pub_ec2_test', 'jw_app_vpc')
        )

        jw_app_pub_subnet1 = ec2.Subnet.from_subnet_attributes(
            self,
            id='JwAppPubSubnet1',
            subnet_id=config.get('pub_ec2_test', 'jw_app_pub_subnet1'),
            availability_zone=config.get('pub_ec2_test', 'az1')
        )

        jw_app_pub_subnet2 = ec2.Subnet.from_subnet_attributes(
            self,
            id='JwAppPubSubnet2',
            subnet_id=config.get('pub_ec2_test', 'jw_app_pub_subnet2'),
            availability_zone=config.get('pub_ec2_test', 'az2')
        )

        jw_app_sg = ec2.SecurityGroup.from_security_group_id(
            self,
            id='JwAppSg',
            security_group_id=config.get('pub_ec2_test', 'jw_app_sg')
        )

        # word_press_pub_ec2_user_data = ec2.UserData.for_linux()
        # word_press_pub_ec2_user_data.add_commands(
        #     'sudo yum install -y httpd mariadb-server'
        # )

        word_press_pub_ec2 = ec2.Instance(
            self,
            id='WordpressPubEc2',
            instance_name='WordpressPubEc2',
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            instance_type=ec2.InstanceType.of(
                instance_class=ec2.InstanceClass.BURSTABLE2,
                instance_size=ec2.InstanceSize.MICRO
            ),
            vpc=jw_app_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[
                    jw_app_pub_subnet1
                ]
            ),
            security_group=jw_app_sg,

            # aws console에서 생성 후 keypair 다운로드
            # local dir ~/.ssh이동
            # chmod 400
            key_name=config.get('pub_ec2_test', 'word_press_pub_ec2_key'),

            # user_data=word_press_pub_ec2_user_data  # user_data를 여기에 추가하는 방법도 있다.
        )

        with open(config.get('pub_ec2_test', 'word_press_pub_ec2_user_data_script'), 'r') as stream:
            user_data = stream.read()
        word_press_pub_ec2.add_user_data(user_data)

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationLoadBalancer.html
        word_press_alb = elbv2.ApplicationLoadBalancer(
            self,
            id='WordPressAlb',
            load_balancer_name='WordPressAlb',
            internet_facing=True,
            # internet_facing=False,
            vpc=jw_app_vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[
                    jw_app_pub_subnet1,
                    jw_app_pub_subnet2
                ]
            ),
            security_group=jw_app_sg
        )

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationTargetGroup.html
        word_press_target_group = elbv2.ApplicationTargetGroup(
            self,
            id='WordPressTargetGroup',
            target_group_name='WordPressTargetGroup',
            # ecs경우에는 IP로 설정후, 아래의 targets param은 없고, 따로 ecs service를 target에 추가했다.
            target_type=elbv2.TargetType.INSTANCE,
            targets=[
                elasticloadbalancingv2_targets.InstanceTarget(
                    word_press_pub_ec2
                )
            ],
            vpc=jw_app_vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,  # Determined from port if known
        )

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationListener.html
        elbv2.ApplicationListener(
            self,
            id='WordPressListener',
            load_balancer=word_press_alb,
            # 실제 웹에서 입력하는 주소에 영향을 준다 (여기만 https/443으로 변경 후 target group은 그대로 두면 https로만 접근가능)
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,  # Default: - Determined from port if known.
            # port=443,
            # protocol=elbv2.ApplicationProtocol.HTTPS,
            # certificates=[deployment_example_certificate],
            # default_action='',  # Cannot be specified together with defaultTargetGroups
            default_target_groups=[
                word_press_target_group
            ]  # Cannot be specified together with defaultAction.
        )