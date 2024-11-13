# eks_cluster.py
from pulumi_aws import eks
from config import cluster_name, node_group_name, k8s_version, instance_type, ami_type, disk_size, capacity_type, desired_size, min_size, max_size
from network import public_subnet_az1, public_subnet_az2, private_subnet_az1, private_subnet_az2
from security import security_group
from iam_roles import eks_role, node_group_role

eks_cluster = eks.Cluster("datareality-dev-safetylab-eks",
    role_arn=eks_role.arn,
    vpc_config=eks.ClusterVpcConfigArgs(
        subnet_ids=[public_subnet_az1.id, public_subnet_az2.id, private_subnet_az1.id, private_subnet_az2.id],
    ),
    version=k8s_version,
    tags={"Name": "datareality-dev-safetylab-eks"}
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
