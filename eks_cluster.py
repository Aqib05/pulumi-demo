import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
import pulumi_eks as eks

# Create a VPC for our cluster
vpc = awsx.ec2.Vpc("vpc")

# Create an IAM role for the EKS cluster
eks_role = aws.iam.Role("eksRole",
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
    }""")

# Attach the necessary policies to the role
role_policy_attachments = [
    aws.iam.RolePolicyAttachment("eksClusterPolicyAttachment",
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
        role=eks_role.id),
    aws.iam.RolePolicyAttachment("eksServicePolicyAttachment",
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy",
        role=eks_role.id)
]

 # Create an EKS cluster with the default configuration.
cluster = aws.ecs.Cluster("my-cluster")

pulumi.export("cluster_name", cluster.name)