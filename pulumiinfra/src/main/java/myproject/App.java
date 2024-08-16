package myproject;

import com.pulumi.Context;
import com.pulumi.Pulumi;
import com.pulumi.aws.eks.Cluster;
import com.pulumi.aws.eks.ClusterArgs;
import com.pulumi.aws.eks.inputs.ClusterVpcConfigArgs;
import com.pulumi.aws.ec2.Vpc;
import com.pulumi.aws.ec2.VpcArgs;
import com.pulumi.aws.ec2.Subnet;
import com.pulumi.aws.ec2.SubnetArgs;
import com.pulumi.core.Output;

import java.util.List;

public class App {
    public static void main(String[] args) {
        Pulumi.run(App::createEKSCluster);
    }

    public static void createEKSCluster(Context ctx) {
        // Create a VPC for the EKS cluster
        var vpc = new Vpc("eks-vpc", VpcArgs.builder()
                .cidrBlock("10.0.0.0/16")
                .build());

        // Create subnets in the VPC
        var subnet1 = new Subnet("subnet1", SubnetArgs.builder()
                .vpcId(vpc.id())
                .cidrBlock("10.0.1.0/24")
                .availabilityZone("us-east-1a")
                .build());

        var subnet2 = new Subnet("subnet2", SubnetArgs.builder()
                .vpcId(vpc.id())
                .cidrBlock("10.0.2.0/24")
                .availabilityZone("us-east-1b")
                .build());

        // Convert List<Output<String>> to Output<List<String>>
        var subnetIds = Output.all(subnet1.id(), subnet2.id());

        // Create the EKS cluster
        var eksCluster = new Cluster("eks-cluster", ClusterArgs.builder()
                .vpcConfig(ClusterVpcConfigArgs.builder()
                        .subnetIds(subnetIds)
                        .build())
                .build());

        // Construct kubeconfig
        var kubeconfig = Output
                .tuple(eksCluster.endpoint(), eksCluster.certificateAuthority().apply(ca -> ca.data()), eksCluster.name())
                .apply(t -> String.format(
                        "apiVersion: v1\n" +
                                "clusters:\n" +
                                "- cluster:\n" +
                                "    server: %s\n" +
                                "    certificate-authority-data: %s\n" +
                                "  name: %s\n" +
                                "contexts:\n" +
                                "- context:\n" +
                                "    cluster: %s\n" +
                                "    user: aws\n" +
                                "  name: %s\n" +
                                "current-context: %s\n" +
                                "kind: Config\n" +
                                "preferences: {}\n" +
                                "users:\n" +
                                "- name: aws\n" +
                                "  user:\n" +
                                "    exec:\n" +
                                "      apiVersion: client.authentication.k8s.io/v1alpha1\n" +
                                "      command: aws-iam-authenticator\n" +
                                "      args:\n" +
                                "        - \"token\"\n" +
                                "        - \"-i\"\n" +
                                "        - \"%s\"\n" +
                                "      env: null\n",
                        t.t1, t.t2, t.t3, t.t3, t.t3, t.t3, t.t3));

        // Export the kubeconfig
        ctx.export("kubeconfig", kubeconfig);
    }
}
