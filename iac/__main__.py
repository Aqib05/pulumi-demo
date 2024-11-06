import pulumi
from pulumi_aws import eks, ec2, iam

# Create a VPC
vpc = ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    tags={"Name": "pulumi-eks-vpc"}
)

# Create public subnets for EKS
public_subnet1 = ec2.Subnet("public-subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone="us-west-2a",
    tags={"Name": "pulumi-eks-public-subnet-1"}
)

public_subnet2 = ec2.Subnet("public-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    map_public_ip_on_launch=True,
    availability_zone="us-west-2b",
    tags={"Name": "pulumi-eks-public-subnet-2"}
)

# Create an EKS Role
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

# Attach the necessary policies to the EKS role
iam.RolePolicyAttachment("eks-cluster-policy",
    role=eks_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
)

iam.RolePolicyAttachment("eks-service-policy",
    role=eks_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
)

# Create the EKS cluster
eks_cluster = eks.Cluster("my-eks-cluster",
    role_arn=eks_role.arn,
    vpc_config=eks.ClusterVpcConfigArgs(
        subnet_ids=[public_subnet1.id, public_subnet2.id]
    ),
    tags={"Name": "pulumi-eks-cluster"}
)

# Create a node group role
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

# Attach necessary policies to the node group role
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

# Create a managed node group
node_group = eks.NodeGroup("my-node-group",
    cluster_name=eks_cluster.name,
    node_group_name="my-node-group",
    node_role_arn=node_group_role.arn,
    subnet_ids=[public_subnet1.id, public_subnet2.id],
    scaling_config=eks.NodeGroupScalingConfigArgs(
        desired_size=2,
        max_size=3,
        min_size=1
    ),
    tags={"Name": "pulumi-eks-node-group"}
)

# Export the cluster's kubeconfig
pulumi.export("kubeconfig", eks_cluster.kubeconfig)
