# config.py

cluster_name = "datareality-dev-eks"
node_group_name = "datareality-dev-eks-ng-public"
instance_type = "t4g.medium"
region = "us-east-2"
k8s_version = "1.31"
ami_type = "AL2_ARM_64"
disk_size = 20
capacity_type = "ON_DEMAND"
desired_size = 2
min_size = 1
max_size = 3
vpc_cidr = "172.20.0.0/16"
public_subnet_cidrs = ["10.0.1.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.2.0/24", "10.0.4.0/24"]
availability_zones = ["us-east-2a", "us-east-2b"]
ssh_key_name = "eks-pulumi-key"
