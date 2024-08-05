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

# Create the EKS cluster
eks_cluster = eks.Cluster("eksCluster",
    role_arn=eks_role.arn,
    vpc_config={
        "subnet_ids": vpc.public_subnet_ids
    })

# Export the kubeconfig for the cluster
pulumi.export("kubeconfig", eks_cluster.kubeconfig)
