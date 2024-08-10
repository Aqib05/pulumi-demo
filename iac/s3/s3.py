# s3/s3.py

import pulumi
import pulumi_aws as aws
from .variables import bucket_name

# Create an S3 bucket
bucket = aws.s3.Bucket(
    "my-bucket",
    bucket=bucket_name,
    tags={
        "Environment": "test",
    }
)

# Export the bucket name
pulumi.export("bucket_name", bucket.bucket)
