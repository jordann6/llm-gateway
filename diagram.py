from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import ECS, Lambda, ECR
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import APIGateway
from diagrams.aws.security import SecretsManager
from diagrams.aws.storage import S3
from diagrams.onprem.client import Users
from diagrams.onprem.network import Internet

graph_attrs = {
    "fontsize": "13",
    "bgcolor": "white",
    "pad": "0.6",
    "splines": "ortho",
    "nodesep": "0.6",
    "ranksep": "0.8",
}

node_attrs = {
    "fontsize": "11",
}

with Diagram(
    "LLM Gateway & Observability Platform",
    filename="docs/architecture",
    outformat="png",
    show=False,
    direction="TB",
    graph_attr=graph_attrs,
    node_attr=node_attrs,
):
    client = Users("Client")

    with Cluster("External LLM Providers"):
        openai = Internet("OpenAI\nGPT-4o-mini")
        anthropic_api = Internet("Anthropic\nClaude Haiku 4.5")

    with Cluster("AWS · us-east-1"):
        apigw = APIGateway("API Gateway\nHTTP API · VPC Link")
        ecr = ECR("ECR\nContainer Image")

        with Cluster("ECS Fargate"):
            ecs = ECS("FastAPI Gateway\nRouting · Caching\nEval Pipeline · Metrics")

        secrets = SecretsManager("Secrets Manager\nAPI Keys · KMS Encrypted")

        with Cluster("DynamoDB"):
            db_log = Dynamodb("Request Log\nrequest_id · timestamp")
            db_cache = Dynamodb("Prompt Cache\nSHA256 hash · TTL")
            db_eval = Dynamodb("Eval Scores\nLLM-as-judge · provider GSI")

        cw = Cloudwatch("CloudWatch\nMetrics · Dashboard\nAlarms · p50/p90/p99")

        with Cluster("Nightly Log Archival"):
            eb = Eventbridge("EventBridge\nNightly Schedule")
            archive_fn = Lambda("Archival Lambda\ngzip NDJSON · S3 partition")

        s3 = S3("S3 Archive\nKMS · Lifecycle Rules\nAthena-compatible")

    client >> apigw >> ecs
    ecr >> Edge(style="dashed") >> ecs
    secrets >> Edge(style="dashed") >> ecs
    ecs >> Edge(label="route") >> openai
    ecs >> Edge(label="route") >> anthropic_api
    ecs >> Edge(label="log") >> db_log
    ecs >> Edge(label="cache") >> db_cache
    ecs >> Edge(label="eval") >> db_eval
    ecs >> Edge(label="metrics") >> cw
    eb >> archive_fn
    archive_fn >> Edge(label="archive") >> s3
    archive_fn >> Edge(label="delete") >> db_log
