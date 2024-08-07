import pulumi
import pulumi_aws as aws
import pulumi_eks as eks

# Configuration variables
config = pulumi.Config()
environment = config.require("environment")

# Create a new VPC
vpc = aws.ec2.Vpc("vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        "Name": f"{environment}-pulumi-vpc",
    })

# Create subnets
subnet = aws.ec2.Subnet("subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    tags={
        "Name": f"{environment}-pulumi-subnet",
    })

# Create an EKS cluster
cluster = eks.Cluster("eks-cluster",
    vpc_id=vpc.id,
    subnet_ids=[subnet.id],
    instance_type="t2.medium",
    desired_capacity=2,
    min_size=1,
    max_size=3,
    tags={
        "Name": f"{environment}-pulumi-eks-cluster",
    })

# Export the kubeconfig
pulumi.export("kubeconfig", cluster.kubeconfig)

