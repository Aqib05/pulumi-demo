package myproject;

import com.pulumi.Context;
import com.pulumi.Pulumi;
import com.pulumi.aws.iam.User;
import com.pulumi.aws.iam.UserArgs;
import com.pulumi.aws.iam.Policy;
import com.pulumi.aws.iam.PolicyArgs;
import com.pulumi.aws.iam.Role;
import com.pulumi.aws.iam.RoleArgs;
import com.pulumi.aws.iam.RolePolicyAttachment;
import com.pulumi.aws.iam.RolePolicyAttachmentArgs;
import com.pulumi.aws.iam.UserPolicyAttachment;
import com.pulumi.aws.iam.UserPolicyAttachmentArgs;

import static com.pulumi.codegen.internal.Serialization.*;

import java.util.Map;

public class App {
    public static void main(String[] args) {
        Pulumi.run(App::stack);
    }

    public static void stack(Context ctx) {
        // Create a new IAM user
        var user = new User("myNewUser", UserArgs.builder()
            .name("my-new-iam-user")  // Specify the IAM user's name
            .build()
        );

        // Export the name of the created user
        ctx.export("userName", user.name());

        // Define and create a new IAM policy
        var policy = new Policy("policy", PolicyArgs.builder()
            .name("test_policy")
            .path("/")
            .description("My test policy")
            .policy(serializeJson(
                jsonObject(
                    jsonProperty("Version", "2012-10-17"),
                    jsonProperty("Statement", jsonArray(jsonObject(
                        jsonProperty("Action", jsonArray("ec2:Describe*")),
                        jsonProperty("Effect", "Allow"),
                        jsonProperty("Resource", "*")
                    )))
                )))
            .build()
        );

        // Export the ARN of the created policy
        ctx.export("policyArn", policy.arn());

        // Define and create a new IAM role
        var role = new Role("testRole", RoleArgs.builder()
            .name("test_role")
            .assumeRolePolicy(serializeJson(
                jsonObject(
                    jsonProperty("Version", "2012-10-17"),
                    jsonProperty("Statement", jsonArray(jsonObject(
                        jsonProperty("Action", "sts:AssumeRole"),
                        jsonProperty("Effect", "Allow"),
                        jsonProperty("Sid", ""),
                        jsonProperty("Principal", jsonObject(
                            jsonProperty("Service", "ec2.amazonaws.com")
                        ))
                    )))
                )))
            .tags(Map.of("tag-key", "tag-value"))
            .build()
        );

        // Export the ARN of the created role
        ctx.export("roleArn", role.arn());

        // Attach the policy to the role
        var rolePolicyAttachment = new RolePolicyAttachment("rolePolicyAttachment", RolePolicyAttachmentArgs.builder()
            .policyArn(policy.arn()) // ARN of the policy to attach
            .role(role.name())      // Name of the role to attach the policy to
            .build()
        );

        // Attach the role to the user
        var userRoleAttachment = new UserPolicyAttachment("userRoleAttachment", UserPolicyAttachmentArgs.builder()
            .policyArn(policy.arn()) // ARN of the policy to attach
            .user(user.name())       // Name of the user to attach the policy to
            .build()
        );

        // Export the ARNs of the role-policy and user-policy attachments
        ctx.export("rolePolicyAttachmentArn", rolePolicyAttachment.id());
        ctx.export("userRoleAttachmentArn", userRoleAttachment.id());
    }
}
