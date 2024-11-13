# load_balancer.py
import pulumi_aws as aws
from network import private_subnet_az1, private_subnet_az2
from security import security_group

private_elb = aws.lb.LoadBalancer("private-elb",
    internal=True,
    load_balancer_type="network",
    subnets=[private_subnet_az1.id, private_subnet_az2.id],
    security_groups=[security_group.id],
    tags={"Name": "private-elb"}
)
