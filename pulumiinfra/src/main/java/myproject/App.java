package myproject;

import com.pulumi.Pulumi;
import com.pulumi.aws.iam.Group;
import com.pulumi.aws.iam.GroupArgs;
import com.pulumi.aws.iam.GroupMembership;
import com.pulumi.aws.iam.GroupMembershipArgs;
import com.pulumi.aws.iam.User;
import com.pulumi.aws.iam.UserArgs;
import com.pulumi.aws.iam.GroupPolicyAttachment;
import com.pulumi.aws.iam.GroupPolicyAttachmentArgs;
import com.pulumi.aws.iam.Policy;
import com.pulumi.aws.iam.PolicyArgs;
import com.pulumi.core.Output;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class App {
    public static void main(String[] args) {
        Pulumi.run(ctx -> {
            // List of user names
            List<String> userNames = Arrays.asList(
                "UmmerShervani",
                "ArunMathev",
                "BijuS",
                "EmilJoseph",
                "VidyothSatesh",
                "AbdullaSoopy",
                "SunithaLakkadan",
                "AjayMani",
                "AkhilR",
                "Akshay",
                "AqibG"
            );

            // Create IAM users
            List<Output<String>> createdUsers = userNames.stream()
                .map(userName -> new User(userName, UserArgs.builder()
                    .name(userName)
                    .build()).name())
                .collect(Collectors.toList());

            // Create IAM Groups with valid names
            Group adminGroup = new Group("adminGroup", GroupArgs.builder().name("Admin").build());
            Group readWriteGroup = new Group("readWriteGroup", GroupArgs.builder().name("Read-Write").build());
            Group readOnlyGroup = new Group("readOnlyGroup", GroupArgs.builder().name("Read-Only").build());

            // Separate users into groups
            List<Output<String>> adminUsers = Arrays.asList(createdUsers.get(0), createdUsers.get(1));
            List<Output<String>> readWriteUsers = Arrays.asList(createdUsers.get(4), createdUsers.get(5), createdUsers.get(6), createdUsers.get(10));
            List<Output<String>> readOnlyUsers = Arrays.asList(createdUsers.get(2), createdUsers.get(3), createdUsers.get(7), createdUsers.get(8), createdUsers.get(9));

            // Assign users to groups
            new GroupMembership("adminGroupMembership", GroupMembershipArgs.builder()
                .group(adminGroup.name())
                .users(Output.all(adminUsers).applyValue(users -> users))
                .build());

            new GroupMembership("readWriteGroupMembership", GroupMembershipArgs.builder()
                .group(readWriteGroup.name())
                .users(Output.all(readWriteUsers).applyValue(users -> users))
                .build());

            new GroupMembership("readOnlyGroupMembership", GroupMembershipArgs.builder()
                .group(readOnlyGroup.name())
                .users(Output.all(readOnlyUsers).applyValue(users -> users))
                .build());

            // Attach the existing AdministratorAccess policy to the Admin group
            new GroupPolicyAttachment("adminPolicyAttachment", GroupPolicyAttachmentArgs.builder()
                .group(adminGroup.name())
                .policyArn("arn:aws:iam::aws:policy/AdministratorAccess")
                .build());

            // Create Read-Write Policy (EKS Full Access)
            Policy readWritePolicy = new Policy("readWritePolicy", PolicyArgs.builder()
                .name("CustomEKSFullAccess")
                .description("Custom policy for EKS full access")
                .policy("{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"eks:*\"],\"Resource\":\"*\"}]}")
                .build());

            // Create Read-Only Policy (EKS Read-Only Access)
            Policy readOnlyPolicy = new Policy("readOnlyPolicy", PolicyArgs.builder()
                .name("CustomEKSReadOnlyAccess")
                .description("Custom policy for EKS read-only access")
                .policy("{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"eks:DescribeCluster\"],\"Resource\":\"*\"}]}")
                .build());

            // Attach custom read-write policy to the Read-Write group
            new GroupPolicyAttachment("readWritePolicyAttachment", GroupPolicyAttachmentArgs.builder()
                .group(readWriteGroup.name())
                .policyArn(readWritePolicy.arn())
                .build());

            // Attach existing read-write policies to the Read-Write group
            List<String> readWritePolicies = Arrays.asList(
                "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
                "arn:aws:iam::aws:policy/AmazonVPCFullAccess",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess",
                "arn:aws:iam::aws:policy/AmazonRDSFullAccess",
                "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
                "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
                "arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess",
                "arn:aws:iam::aws:policy/CloudWatchFullAccess"
            );

            readWritePolicies.forEach(policyArn -> new GroupPolicyAttachment("readWritePolicyAttachment" + policyArn.hashCode(),
                GroupPolicyAttachmentArgs.builder()
                    .group(readWriteGroup.name())
                    .policyArn(policyArn)
                    .build()));

            // Attach custom read-only policy to the Read-Only group
            new GroupPolicyAttachment("readOnlyPolicyAttachment", GroupPolicyAttachmentArgs.builder()
                .group(readOnlyGroup.name())
                .policyArn(readOnlyPolicy.arn())
                .build());

            // Attach existing read-only policies to the Read-Only group
            List<String> readOnlyPolicies = Arrays.asList(
                "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonVPCReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
                "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonRDSReadOnlyAccess",
                "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess",
                "arn:aws:iam::aws:policy/AWSLambda_ReadOnlyAccess",
                "arn:aws:iam::aws:policy/ElasticLoadBalancingReadOnlyAccess",
                "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
            );

            readOnlyPolicies.forEach(policyArn -> new GroupPolicyAttachment("readOnlyPolicyAttachment" + policyArn.hashCode(),
                GroupPolicyAttachmentArgs.builder()
                    .group(readOnlyGroup.name())
                    .policyArn(policyArn)
                    .build()));

            // Export group names
            ctx.export("AdminGroup", adminGroup.name());
            ctx.export("ReadWriteGroup", readWriteGroup.name());
            ctx.export("ReadOnlyGroup", readOnlyGroup.name());
        });
    }
}
