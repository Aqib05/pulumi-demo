# iam_roles.py
import pulumi_aws as aws

# EKS Cluster Role
eks_role = aws.iam.Role("eksRole", assume_role_policy="""{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "eks.amazonaws.com"}, "Action": "sts:AssumeRole"}]
}""")
aws.iam.RolePolicyAttachment("eks-cluster-policy", role=eks_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy")
aws.iam.RolePolicyAttachment("eks-service-policy", role=eks_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy")

# Node Group Role
node_group_role = aws.iam.Role("nodeGroupRole", assume_role_policy="""{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]
}""")
aws.iam.RolePolicyAttachment("node-group-policy", role=node_group_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy")
aws.iam.RolePolicyAttachment("cni-policy", role=node_group_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy")
aws.iam.RolePolicyAttachment("ec2-container-registry-policy", role=node_group_role.name, policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly")
