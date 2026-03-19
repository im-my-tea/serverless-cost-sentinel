# Serverless Cost Sentinel

![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?style=for-the-badge&logo=amazon-aws)
![EventBridge](https://img.shields.io/badge/AWS-EventBridge-FF4F8B?style=for-the-badge&logo=amazon-aws)
![Terraform](https://img.shields.io/badge/Terraform-IaC-623CE4?style=for-the-badge&logo=terraform)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)

An event-driven Lambda that scans all AWS regions daily and stops 
idle EC2 instances tagged as dev/test environments. Deployed via 
Terraform. Architecture diagram in `Cost Optimizer.excalidraw`.

---

## Architecture
```
EventBridge (cron: midnight UTC)
        │
        ▼
Lambda (python3.12, 300s timeout)
        │
        ├── get_all_regions()          ← ec2:DescribeRegions
        │
        └── ThreadPoolExecutor (×10)   ← 15+ regions in parallel
                │
                └── process_region()
                        ├── get_running_instances()  ← paginator + generator
                        └── stop_instances()          ← ec2:StopInstances
                                │
                                ▼
                        CloudWatch Logs
```

---

## Key engineering decisions

**Concurrent region scanning**
`ThreadPoolExecutor(max_workers=10)` processes 10 regions 
simultaneously. Sequential scanning at ~2s/region across 15+ 
regions would take 30+ seconds. Concurrent execution brings 
this to ~4 seconds — important since Lambda bills per millisecond.

**Generator + paginator pattern**
`get_running_instances` uses a paginator (handles AWS's 1000-result 
page limit automatically) and yields instance IDs one at a time. 
Memory usage stays flat regardless of how many instances exist 
across all regions.

**Custom decorators for cross-cutting concerns**
`@handle_aws_errors` — catches `ClientError`, `BotoCoreError`, 
and unexpected exceptions. Returns `None` cleanly instead of 
crashing the Lambda.  
`@log_execution_time` — logs duration of expensive operations 
to CloudWatch for observability.

**Tag-based targeting**
Instances are filtered by `TAG_KEY` / `TAG_VALUE` environment 
variables (default: `Environment=Dev`). Only tagged dev instances 
are stopped — production is never touched.

---

## Terraform deployment
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Resources provisioned:
- Lambda function (python3.12, 300s timeout)
- IAM role with least-privilege EC2 + CloudWatch permissions
- EventBridge cron rule (midnight UTC daily)
- Lambda permission allowing EventBridge invocation

To tear down:
```bash
terraform destroy
```

---

## Project structure
```
src/
├── lambda_function.py   # handler + ThreadPoolExecutor orchestration
├── ec2_manager.py       # EC2 API calls (paginator, stop logic)
└── decorators.py        # @handle_aws_errors, @log_execution_time

terraform/
├── main.tf              # Lambda, IAM, EventBridge resources
├── variables.tf         # region, project_name, tag_key, tag_value
└── outputs.tf           # Lambda ARN, EventBridge ARN, IAM role ARN

tests/                   # unit tests
```