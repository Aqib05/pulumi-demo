import pulumi
import pulumi_aws as aws

# Fetch the default VPC
default_vpc = aws.ec2.get_vpc(default=True)

# Fetch subnets in the default VPC
subnets = aws.ec2.get_subnets(filters=[{
    "name": "vpc-id",
    "values": [default_vpc.id]
}])

# Get the most recent Ubuntu 22.04 AMI
ubuntu = aws.ec2.get_ami(most_recent=True,
    filters=[
        {
            "name": "name",
            "values": ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"],
        },
        {
            "name": "virtualization-type",
            "values": ["hvm"],
        },
    ],
    owners=["amazon"])

# Create a security group
security_group = aws.ec2.SecurityGroup('web-secgrp',
    description='Enable SSH access',
    ingress=[{
        'protocol': 'tcp',
        'from_port': 22,
        'to_port': 22,
        'cidr_blocks': ['0.0.0.0/0'],
    }]
)

# Create the EC2 instance
web = aws.ec2.Instance("web",
    ami=ubuntu.id,
    instance_type=aws.ec2.InstanceType.T3_MICRO,
    subnet_id=subnets.ids[0],  # Specify the first subnet in the default VPC
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "pulumiEc2",
    })

# Export the resulting instance's public IP address and DNS name
pulumi.export('public_ip', web.public_ip)
pulumi.export('public_dns', web.public_dns)
