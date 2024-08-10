# vpc/vpc.py

import pulumi
import pulumi_aws as aws
from .variables import vpc_cidr

# Create a VPC
vpc = aws.ec2.Vpc(
    "my-vpc",
    cidr_block=vpc_cidr,
    tags={
        "Name": "my-vpc",
    }
)

# Export the VPC ID
pulumi.export("vpc_id", vpc.id)
