from pathlib import Path

from aws_cdk import Stack, CfnOutput
from aws_cdk.aws_bedrock_agentcore_alpha import Memory, Runtime, AgentRuntimeArtifact
from aws_cdk.aws_ecr_assets import DockerImageAsset, Platform
from aws_cdk.aws_iam import PolicyStatement
from constructs import Construct

FOUNDATIONAL_MODEL = "amazon.nova-2-lite-v1:0"
INFERENCE_PROFILE = f"global.{FOUNDATIONAL_MODEL}"

class AgentcoreStack(Stack):
    """
    CDK stack that deploys a Bedrock AgentCore runtime, its backing memory store,
    and a custom agent image hosted in Amazon ECR.

    This stack performs the following:
    - Creates a persistent Memory instance used by the AgentCore runtime.
    - Builds and publishes the agent Docker image from the local `assets` directory.
    - Deploys an Agent Runtime configured to use the built image.
    - Grants the runtime permission to access the memory store.
    - Outputs the Agent Runtime ARN for use when invoking the deployed agent.
    """

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            **kwargs
    ) -> None:
        """
        Initialize the AgentCore stack.
        :param scope: The parent Construct.
        :param construct_id: The logical identifier for this stack.
        :param kwargs: Additional Stack properties.
        """
        super().__init__(scope, construct_id, **kwargs)

        # initiate memory store
        memory = Memory(
            scope=self,
            id="Memory",
            memory_name="memory"
        )

        # build agent image
        agent_assets = Path(__file__).parents[1].joinpath("assets")
        agent_image = DockerImageAsset(
            scope=self,
            id="Agent",
            directory=str(agent_assets),
            platform=Platform.LINUX_ARM64
        )

        # initiate agent runtime
        runtime = Runtime(
            scope=self,
            id="Runtime",
            runtime_name="Agent",
            agent_runtime_artifact=AgentRuntimeArtifact.from_ecr_repository(
                repository=agent_image.repository,
                tag=agent_image.image_tag
            ),
            environment_variables={
                'MEMORY_ID': memory.memory_id,
                'MODEL_ID': INFERENCE_PROFILE,
                'AWS_DEFAULT_REGION': self.region
            }
        )

        # grant runtime necessary rights
        memory.grant_full_access(runtime)
        runtime.role.add_to_principal_policy(
            PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}:{self.account}:inference-profile/{INFERENCE_PROFILE}",
                    f"arn:aws:bedrock:{self.region}::foundation-model/{FOUNDATIONAL_MODEL}",
                    f"arn:aws:bedrock:::foundation-model/{FOUNDATIONAL_MODEL}",
                ],
            )
        )

        # expose runtime ARN
        CfnOutput(
            scope=self,
            id="RuntimeArn",
            value=runtime.agent_runtime_arn,
            description="ARN of the Bedrock Agent Runtime used for invoking the deployed agent.",
        )
