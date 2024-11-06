import pulumi
import pulumi_aws as aws
import pulumi_kubernetes as k8s
import pulumi_eks as eks

# Create a VPC
vpc = aws.ec2.Vpc(
    resource_name='my-vpc',
    cidr_block='10.0.0.0/16',
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={
        'Name': 'my-vpc',
    }
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway(
    resource_name='my-igw',
    vpc_id=vpc.id,
    tags={
        'Name': 'my-igw',
    }
)

# Create Public Subnets
public_subnet_1 = aws.ec2.Subnet(
    resource_name='my-public-subnet-1',
    vpc_id=vpc.id,
    cidr_block='10.0.1.0/24',
    map_public_ip_on_launch=True,
    availability_zone='ap-south-1a',
    tags={
        'Name': 'my-public-subnet-1',
    }
)

public_subnet_2 = aws.ec2.Subnet(
    resource_name='my-public-subnet-2',
    vpc_id=vpc.id,
    cidr_block='10.0.2.0/24',
    map_public_ip_on_launch=True,
    availability_zone='ap-south-1b',
    tags={
        'Name': 'my-public-subnet-2',
    }
)

# Create Private Subnets
private_subnet_1 = aws.ec2.Subnet(
    resource_name='my-private-subnet-1',
    vpc_id=vpc.id,
    cidr_block='10.0.3.0/24',
    map_public_ip_on_launch=False,
    availability_zone='ap-south-1a',
    tags={
        'Name': 'my-private-subnet-1',
    }
)

private_subnet_2 = aws.ec2.Subnet(
    resource_name='my-private-subnet-2',
    vpc_id=vpc.id,
    cidr_block='10.0.4.0/24',
    map_public_ip_on_launch=False,
    availability_zone='ap-south-1b',
    tags={
        'Name': 'my-private-subnet-2',
    }
)

# Create a Public Route Table
public_route_table = aws.ec2.RouteTable(
    resource_name='my-public-route-table',
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block='0.0.0.0/0',
            gateway_id=internet_gateway.id,
        )
    ],
    tags={
        'Name': 'my-public-route-table',
    }
)

# Associate the Public Route Table with Public Subnets
public_route_table_association_1 = aws.ec2.RouteTableAssociation(
    resource_name='my-public-route-table-association-1',
    subnet_id=public_subnet_1.id,
    route_table_id=public_route_table.id,
)

public_route_table_association_2 = aws.ec2.RouteTableAssociation(
    resource_name='my-public-route-table-association-2',
    subnet_id=public_subnet_2.id,
    route_table_id=public_route_table.id,
)

# Create a NAT Gateway for Private Subnets
eip = aws.ec2.Eip('my-eip', vpc=True)

nat_gateway = aws.ec2.NatGateway(
    resource_name='my-nat-gateway',
    subnet_id=public_subnet_1.id,
    allocation_id=eip.id,
    tags={
        'Name': 'my-nat-gateway',
    }
)

# Create a Private Route Table
private_route_table = aws.ec2.RouteTable(
    resource_name='my-private-route-table',
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block='0.0.0.0/0',
            nat_gateway_id=nat_gateway.id,
        )
    ],
    tags={
        'Name': 'my-private-route-table',
    }
)

# Associate the Private Route Table with Private Subnets
private_route_table_association_1 = aws.ec2.RouteTableAssociation(
    resource_name='my-private-route-table-association-1',
    subnet_id=private_subnet_1.id,
    route_table_id=private_route_table.id,
)

private_route_table_association_2 = aws.ec2.RouteTableAssociation(
    resource_name='my-private-route-table-association-2',
    subnet_id=private_subnet_2.id,
    route_table_id=private_route_table.id,
)

# Create an EKS Cluster
eks_cluster = eks.Cluster('my-cluster',
    vpc_id=vpc.id,
    public_subnet_ids=[public_subnet_1.id, public_subnet_2.id],
    private_subnet_ids=[private_subnet_1.id, private_subnet_2.id],
    instance_type='t2.medium',
    desired_capacity=2,
    min_size=1,
    max_size=3
)

# Export the kubeconfig to access the cluster
pulumi.export('kubeconfig', eks_cluster.kubeconfig)
