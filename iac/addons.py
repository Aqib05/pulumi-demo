# addons.py
import pulumi_aws as aws
from eks_cluster import eks_cluster

ebs_csi_driver_addon = aws.eks.Addon("ebs-csi-driver",
    addon_name="aws-ebs-csi-driver",
    cluster_name=eks_cluster.name,
    resolve_conflicts_on_create="OVERWRITE",
    resolve_conflicts_on_update="PRESERVE"
)
