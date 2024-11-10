import pulumi
import pulumi_aws as aws
from pulumi_aws import eks, ec2, iam

# Configuration Variables
cluster_name = "ai-engineering-safetylab-eks"
node_group_name = "ai-engineering-eks-ng-public"
instance_type = "t3.medium"
region = "us-east-2"
k8s_version = "1.24"
ami_type = "AL2_x86_64"
disk_size = 20
capacity_type = "ON_DEMAND"
desired_size = 2
min_size = 1
max_size = 3
vpc_cidr = "172.20.0.0/16"

# Create a VPC
vpc = aws.ec2.Vpc(
    "ai-safetylab-eks-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "ai-safetylab-eks-vpc"}
)

# Internet Gateway for Public Subnets
internet_gateway = aws.ec2.InternetGateway(
    "ai-safetylab-eks-igw",
    vpc_id=vpc.id,
    tags={"Name": "ai-safetylab-eks-igw"}
)

# Elastic IP for NAT Gateway
eip = aws.ec2.Eip("ai-safetylab-eks-eip", tags={"Name": "ai-safetylab-eks-eip"}, domain="vpc")

# Public and Private Subnets
public_subnet_az1 = aws.ec2.Subnet(
    "ai-safetylab-eks-public-subnet-az1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-2a",
    map_public_ip_on_launch=True,
    tags={"Name": "ai-safetylab-eks-public-subnet-az1"}
)
public_subnet_az2 = aws.ec2.Subnet(
    "ai-safetylab-eks-public-subnet-az2",
    vpc_id=vpc.id,
    cidr_block="10.0.3.0/24",
    availability_zone="us-east-2b",
    map_public_ip_on_launch=True,
    tags={"Name": "ai-safetylab-eks-public-subnet-az2"}
)
private_subnet_az1 = aws.ec2.Subnet(
    "ai-safetylab-eks-private-subnet-az1",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-east-2a",
    tags={"Name": "ai-safetylab-eks-private-subnet-az1"}
)
private_subnet_az2 = aws.ec2.Subnet(
    "ai-safetylab-eks-private-subnet-az2",
    vpc_id=vpc.id,
    cidr_block="10.0.4.0/24",
    availability_zone="us-east-2b",
    tags={"Name": "ai-safetylab-eks-private-subnet-az2"}
)

# Public Route Table and Associations
public_route_table = aws.ec2.RouteTable(
    "ai-safetylab-eks-public-rt",
    vpc_id=vpc.id,
    tags={"Name": "ai-safetylab-eks-public-rt"}
)
public_route = aws.ec2.Route(
    "ai-safetylab-eks-public-route",
    route_table_id=public_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=internet_gateway.id
)
aws.ec2.RouteTableAssociation("ai-safetylab-eks-public-rt-assoc-az1", subnet_id=public_subnet_az1.id, route_table_id=public_route_table.id)
aws.ec2.RouteTableAssociation("ai-safetylab-eks-public-rt-assoc-az2", subnet_id=public_subnet_az2.id, route_table_id=public_route_table.id)

# Private Route Table and NAT Gateway
private_route_table = aws.ec2.RouteTable(
    "ai-safetylab-eks-private-rt",
    vpc_id=vpc.id,
    tags={"Name": "ai-safetylab-eks-private-rt"}
)
nat_gateway = aws.ec2.NatGateway(
    "ai-safetylab-eks-nat-gateway",
    subnet_id=public_subnet_az1.id,
    allocation_id=eip.id,
    tags={"Name": "ai-safetylab-eks-nat-gateway"}
)
private_route = aws.ec2.Route(
    "ai-safetylab-eks-private-route",
    route_table_id=private_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=nat_gateway.id
)
aws.ec2.RouteTableAssociation("ai-safetylab-eks-private-rt-assoc-az1", subnet_id=private_subnet_az1.id, route_table_id=private_route_table.id)
aws.ec2.RouteTableAssociation("ai-safetylab-eks-private-rt-assoc-az2", subnet_id=private_subnet_az2.id, route_table_id=private_route_table.id)

# Security Group
security_group = ec2.SecurityGroup(
    "cluster-security-group",
    vpc_id=vpc.id,
    description="EKS cluster security group",
    ingress=[
        ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=0,
            to_port=65535,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={"Name": f"{cluster_name}-security-group"}
)

# EKS Cluster Role and Node Group Role with Policies
eks_role = iam.Role("eksRole", assume_role_policy="""{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "eks.amazonaws.com"}, "Action": "sts:AssumeRole"}]
}""")
iam.RolePolicyAttachment("eks-cluster-policy", role=eks_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy")
iam.RolePolicyAttachment("eks-service-policy", role=eks_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy")

# Node Group Role with Policies
node_group_role = iam.Role("nodeGroupRole", assume_role_policy="""{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]
}""")
iam.RolePolicyAttachment("node-group-policy", role=node_group_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy")
iam.RolePolicyAttachment("cni-policy", role=node_group_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy")
iam.RolePolicyAttachment("ec2-container-registry-policy", role=node_group_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly")


# EKS Cluster and Node Group
eks_cluster = eks.Cluster("ai-engineering-safetylab-eks",
    role_arn=eks_role.arn,
    vpc_config=eks.ClusterVpcConfigArgs(
        subnet_ids=[public_subnet_az1.id, public_subnet_az2.id, private_subnet_az1.id, private_subnet_az2.id],
    ),
    version=k8s_version,
    tags={"Name": "ai-engineering-safetylab-eks"}
)

node_group = eks.NodeGroup(node_group_name,
    cluster_name=eks_cluster.name,
    node_role_arn=node_group_role.arn,
    subnet_ids=[public_subnet_az1.id, public_subnet_az2.id],
    scaling_config=eks.NodeGroupScalingConfigArgs(
        desired_size=desired_size,
        max_size=max_size,
        min_size=min_size
    ),
    instance_types=[instance_type],
    ami_type=ami_type,
    disk_size=disk_size,
    capacity_type=capacity_type,
    remote_access=eks.NodeGroupRemoteAccessArgs(
        ec2_ssh_key="eks-pulumi-key",
        source_security_group_ids=[security_group.id]
    ),
    tags={"Name": node_group_name}
)

# Amazon EBS CSI Driver Add-on with proper cluster reference and conflict resolution
ebs_csi_driver_addon = aws.eks.Addon("ebs-csi-driver",
    addon_name="aws-ebs-csi-driver",
    cluster_name=eks_cluster.name,  # Corrected to reference eks_cluster
    resolve_conflicts_on_create="OVERWRITE",  # Specify conflict handling on create
    resolve_conflicts_on_update="PRESERVE"    # Specify conflict handling on update
)



# Private Elastic Load Balancer
private_elb = aws.lb.LoadBalancer("private-elb",
    internal=True,
    load_balancer_type="network",
    subnets=[private_subnet_az1.id, private_subnet_az2.id],
    security_groups=[security_group.id],
    tags={"Name": "private-elb"}
)

# Export Outputs
pulumi.export("vpc_id", vpc.id)
pulumi.export("eks_cluster_name", eks_cluster.name)
pulumi.export("private_elb_dns", private_elb.dns_name)
