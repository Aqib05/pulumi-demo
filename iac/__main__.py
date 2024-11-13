# __main__.py
import pulumi
from network import vpc
from eks_cluster import eks_cluster
from load_balancer import private_elb

pulumi.export("vpc_id", vpc.id)
pulumi.export("eks_cluster_name", eks_cluster.name)
pulumi.export("private_elb_dns", private_elb.dns_name)
