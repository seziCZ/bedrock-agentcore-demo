import aws_cdk as core
import aws_cdk.assertions as assertions
import pytest
from aws_cdk.assertions import Template

from agentcore.stack import AgentCoreStack


@pytest.fixture
def template() -> Template:
    """
    Creates a CDK application and synthesizes the AgentcoreStack
    into a CloudFormation template for assertions.
    """
    app = core.App()
    stack = AgentCoreStack(app, "agentcore")
    return assertions.Template.from_stack(stack)


def test_memory(template: Template) -> None:
    """
    Verifies that the stack defines a Bedrock AgentCore Memory
    resource with the expected configuration.
    """
    template.has_resource_properties(
        type="AWS::BedrockAgentCore::Memory",
        props={
            "EventExpiryDuration": 90,
            "Name": "memory",
        },
    )


def test_runtime(template: Template) -> None:
    """
    Ensures that the stack creates a Bedrock AgentCore Runtime
    with the correct settings for name, protocol, and networking.
    """
    template.has_resource_properties(
        type="AWS::BedrockAgentCore::Runtime",
        props={
            "AgentRuntimeName": "Agent",
            "ProtocolConfiguration": "HTTP",
            "NetworkConfiguration": {
                "NetworkMode": "PUBLIC"
            },
        },
    )
