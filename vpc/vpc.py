import json
from typing import Optional, TypedDict

import pulumi
from pulumi import ResourceOptions
from pulumi_aws import ec2

class VpcArgs(TypedDict):
    vpc_name: pulumi.Input[str]
    cidr_block: pulumi.Input[str]
    tags_additional: pulumi.Input[dict[str, pulumi.Input[str]]]
    igw_name: pulumi.Input[str]

class Vpc(pulumi.ComponentResource):
    vpc_id: pulumi.Output[str]

    def __init__(self,
                 name: str,
                 args: VpcArgs,
                 opts: Optional[ResourceOptions] = None) -> None:

        super().__init__('vpc:index:Vpc', name, {}, opts)

        base_tags = {
            "Name": args.get("vpc_name"),
            # Add other static tags here if needed
        }

        # Merge base_tags with tags_additional if provided
        all_tags = pulumi.Output.all(base_tags, args.get("tags_additional")).apply(
            lambda items: {**items[0], **(items[1] or {})}
        )

        vpc = ec2.Vpc(
            args.get("vpc_name"),
            cidr_block=args.get("cidr_block"),
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags=all_tags,
        )
        
        self.vpc_id = vpc.id

        # By registering the outputs on which the component depends, we ensure
        # that the Pulumi CLI will wait for all the outputs to be created before
        # considering the component itself to have been created.
        self.register_outputs({
            'vpc_id': vpc.id,
        })

        # Internet Gateway
        internet_gateway = ec2.InternetGateway(
            "internetGateway", vpc_id=vpc.id, tags={"Name": args.get("igw_name")}
        )

