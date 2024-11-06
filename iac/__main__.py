import pulumi
import pulumi_aws
from pulumi_aws import eks, ec2, iam
import base64

# VPC Configuration Variables
vpc_cidr = "10.0.0.0/16"
region = "us-east-2"
public_subnet_cidrs = ["10.0.1.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.2.0/24", "10.0.4.0/24"]

# Cluster and Node Group Configuration Variables
cluster_name = "ai-engineering-safetylab-eks"
node_group_name = "ai-engineering-eks-ng-public"
instance_type = "t3.medium"
k8s_version = "1.24"
ami_type = "AL2_x86_64"
disk_size = 20
capacity_type = "ON_DEMAND"
desired_size = 2
min_size = 1
max_size = 3

# Create VPC
vpc = ec2.Vpc("ai-vpc",
    cidr_block=vpc_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": f"{cluster_name}-vpc"}
)

# Internet Gateway for Public Subnets
igw = ec2.InternetGateway("ai-internet-gateway",
    vpc_id=vpc.id,
    tags={"Name": f"{cluster_name}-igw"}
)

# NAT Gateway and Elastic IP for Private Subnets
eip = ec2.Eip("ai-nat-gateway-eip", 
    tags={"Name": f"{cluster_name}-nat-eip"}
)

nat_gateway = ec2.NatGateway("ai-nat-gateway",
    allocation_id=eip.id,
    subnet_id=public_subnet_cidrs[0],  # NAT Gateway in the first public subnet
    tags={"Name": f"{cluster_name}-nat-gateway"}
)

# Create Subnets (Public and Private)
public_subnet_1 = ec2.Subnet("ai-public-subnet-1",
    vpc_id=vpc.id,
    cidr_block=public_subnet_cidrs[0],
    map_public_ip_on_launch=True,
    availability_zone=f"{region}a",
    tags={"Name": f"{cluster_name}-ai-public-subnet-1"}
)

public_subnet_2 = ec2.Subnet("ai-public-subnet-2",
    vpc_id=vpc.id,
    cidr_block=public_subnet_cidrs[1],
    map_public_ip_on_launch=True,
    availability_zone=f"{region}b",
    tags={"Name": f"{cluster_name}-ai-public-subnet-2"}
)

private_subnet_1 = ec2.Subnet("ai-private-subnet-1",
    vpc_id=vpc.id,
    cidr_block=private_subnet_cidrs[0],
    availability_zone=f"{region}a",
    tags={"Name": f"{cluster_name}-ai-private-subnet-1"}
)

private_subnet_2 = ec2.Subnet("ai-private-subnet-2",
    vpc_id=vpc.id,
    cidr_block=private_subnet_cidrs[1],
    availability_zone=f"{region}b",
    tags={"Name": f"{cluster_name}-ai-private-subnet-2"}
)

# Route Table for Public Subnets
public_route_table = ec2.RouteTable("ai-public-route-table",
    vpc_id=vpc.id,
    routes=[ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id
    )],
    tags={"Name": f"{cluster_name}-ai-public-rt"}
)

# Route Table for Private Subnets
private_route_table = ec2.RouteTable("ai-private-route-table",
    vpc_id=vpc.id,
    routes=[ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        nat_gateway_id=nat_gateway.id
    )],
    tags={"Name": f"{cluster_name}-ai-private-rt"}
)

# Associate Route Tables with Subnets
ec2.RouteTableAssociation("ai-public-subnet-1-rt-association",
    subnet_id=public_subnet_1.id,
    route_table_id=public_route_table.id
)

ec2.RouteTableAssociation("ai-public-subnet-2-rt-association",
    subnet_id=public_subnet_2.id,
    route_table_id=public_route_table.id
)

ec2.RouteTableAssociation("ai-private-subnet-1-rt-association",
    subnet_id=private_subnet_1.id,
    route_table_id=private_route_table.id
)

ec2.RouteTableAssociation("ai-private-subnet-2-rt-association",
    subnet_id=private_subnet_2.id,
    route_table_id=private_route_table.id
)

# Create EKS Role
eks_role = iam.Role("eksRole",
    assume_role_policy="""{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "eks.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }"""
)

# Attach Policies to EKS Role
iam.RolePolicyAttachment("eks-cluster-policy",
    role=eks_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
)

iam.RolePolicyAttachment("eks-service-policy",
    role=eks_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
)

# Create EKS Cluster
eks_cluster = eks.Cluster(cluster_name,
    role_arn=eks_role.arn,
    version=k8s_version,
    vpc_config=eks.ClusterVpcConfigArgs(
        subnet_ids=[public_subnet_1.id, public_subnet_2.id, private_subnet_1.id, private_subnet_2.id],
        endpoint_public_access=True,
        public_access_cidrs=["0.0.0.0/0"]
    ),
    tags={"Name": cluster_name}
)

# Node Group Role
node_group_role = iam.Role("nodeGroupRole",
    assume_role_policy="""{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "ec2.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }"""
)

# Attach Policies to Node Group Role
iam.RolePolicyAttachment("node-group-policy",
    role=node_group_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
)

iam.RolePolicyAttachment("cni-policy",
    role=node_group_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSCNIPolicy"
)

iam.RolePolicyAttachment("ec2-container-registry-policy",
    role=node_group_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
)

# Create Node Group
node_group = eks.NodeGroup(node_group_name,
    cluster_name=eks_cluster.name,
    node_group_name=node_group_name,
    node_role_arn=node_group_role.arn,
    subnet_ids=[public_subnet_1.id, public_subnet_2.id, private_subnet_1.id, private_subnet_2.id],
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
        source_security_group_ids=[eks_cluster.vpc_config.cluster_security_group_id]
    ),
    tags={"Name": node_group_name}
)

# Correctly exporting kubeconfig
kubeconfig = pulumi.Output.all(eks_cluster.endpoint, eks_cluster.certificate_authority, eks_cluster.name).apply(
    lambda args: f"""apiVersion: v1
clusters:
- cluster:
    server: {args[0]}
    certificate-authority-data: {args[1]['data']}
  name: {args[2]}
contexts:
- context:
    cluster: {args[2]}
    user: {args[2]}
  name: {args[2]}
current-context: {args[2]}
kind: Config
preferences: {{}}
users:
- name: {args[2]}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: aws
      args:
        - "eks"
        - "get-token"
        - "--cluster-name"
        - "{args[2]}"
      env:
        - name: "AWS_PROFILE"
          value: "default"
    """
)

pulumi.export("kubeconfig", kubeconfig)
