#!/usr/bin/env python3
import aws_cdk as cdk

from agentcore.stack import AgentcoreStack


app = cdk.App()

# Optionally specify an environment (uncomment if needed)
# env = cdk.Environment(
#     account=os.getenv("CDK_DEFAULT_ACCOUNT"),
#     region=os.getenv("CDK_DEFAULT_REGION")
# )
# AgentcoreStack(app, "AgentcorePocStack", env=env)

AgentcoreStack(app, "AgentcoreStack")

app.synth()