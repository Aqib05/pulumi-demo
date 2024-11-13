# network.py
import pulumi_aws as aws
from config import cluster_name

# Create a VPC
vpc = aws.ec2.Vpc(
    "datareality-dev-eks-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "datareality-dev-eks-vpc"}
)

# Internet Gateway for Public Subnets
internet_gateway = aws.ec2.InternetGateway(
    "datareality-dev-eks-igw",
    vpc_id=vpc.id,
    tags={"Name": "datareality-dev-eks-igw"}
)

# Elastic IP for NAT Gateway
eip = aws.ec2.Eip("datareality-dev-eks-eip", tags={"Name": "datareality-dev-eks-eip"}, domain="vpc")

# Public and Private Subnets
public_subnet_az1 = aws.ec2.Subnet(
    "datareality-dev-eks-public-subnet-az1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-2a",
    map_public_ip_on_launch=True,
    tags={"Name": "datareality-dev-eks-public-subnet-az1"}
)
public_subnet_az2 = aws.ec2.Subnet(
    "datareality-dev-eks-public-subnet-az2",
    vpc_id=vpc.id,
    cidr_block="10.0.3.0/24",
    availability_zone="us-east-2b",
    map_public_ip_on_launch=True,
    tags={"Name": "datareality-dev-eks-public-subnet-az2"}
)
private_subnet_az1 = aws.ec2.Subnet(
    "datareality-dev-eks-private-subnet-az1",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-east-2a",
    tags={"Name": "datareality-dev-eks-private-subnet-az1"}
)
private_subnet_az2 = aws.ec2.Subnet(
    "datareality-dev-eks-private-subnet-az2",
    vpc_id=vpc.id,
    cidr_block="10.0.4.0/24",
    availability_zone="us-east-2b",
    tags={"Name": "datareality-dev-eks-private-subnet-az2"}
)

# Public Route Table and Associations
public_route_table = aws.ec2.RouteTable(
    "datareality-dev-eks-public-rt",
    vpc_id=vpc.id,
    tags={"Name": "datareality-dev-eks-public-rt"}
)
public_route = aws.ec2.Route(
    "datareality-dev-eks-public-route",
    route_table_id=public_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internet_gateway.id
)
aws.ec2.RouteTableAssociation("datareality-dev-eks-public-rt-assoc-az1", subnet_id=public_subnet_az1.id, route_table_id=public_route_table.id)
aws.ec2.RouteTableAssociation("datareality-dev-eks-public-rt-assoc-az2", subnet_id=public_subnet_az2.id, route_table_id=public_route_table.id)

# Private Route Table and NAT Gateway
private_route_table = aws.ec2.RouteTable(
    "datareality-dev-eks-private-rt",
    vpc_id=vpc.id,
    tags={"Name": "datareality-dev-eks-private-rt"}
)
nat_gateway = aws.ec2.NatGateway(
    "datareality-dev-eks-nat-gateway",
    subnet_id=public_subnet_az1.id,
    allocation_id=eip.id,
    tags={"Name": "datareality-dev-eks-nat-gateway"}
)
private_route = aws.ec2.Route(
    "datareality-dev-eks-private-route",
    route_table_id=private_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=nat_gateway.id
)
aws.ec2.RouteTableAssociation("datareality-dev-eks-private-rt-assoc-az1", subnet_id=private_subnet_az1.id, route_table_id=private_route_table.id)
aws.ec2.RouteTableAssociation("datareality-dev-eks-private-rt-assoc-az2", subnet_id=private_subnet_az2.id, route_table_id=private_route_table.id)
