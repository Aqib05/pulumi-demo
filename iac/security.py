# security.py
import pulumi_aws as aws
from config import cluster_name
from network import vpc

security_group = aws.ec2.SecurityGroup(
    "cluster-security-group",
    vpc_id=vpc.id,
    description="EKS cluster security group",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=0,
            to_port=65535,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={"Name": f"{cluster_name}-security-group"}
)
