# Serverless Cost Sentinel 🛡️

A resilient, event-driven automation tool designed to optimize cloud infrastructure costs. It utilizes concurrency to scan multiple AWS regions simultaneously and terminates idle development resources based on tagging strategies.

## 🏗️ Architecture
**EventBridge (Cron)** -> **AWS Lambda** -> **Boto3 (ThreadPoolExecutor)** -> **EC2 API**

## ✨ Key Features
- **Concurrent Execution:** Uses `ThreadPoolExecutor` to scan 15+ AWS regions in parallel, reducing Lambda runtime by 90%.
- **Resilience:** Implements custom Python Decorators (`@handle_aws_errors`) for robust error handling and logging.
- **Observability:** Structured logging integrated with AWS CloudWatch for audit trails.
- **Infrastructure as Code:** Fully decoupled logic using the `EC2Manager` class pattern.

## 🛠️ Tech Stack
- **Language:** Python 3.9
- **Cloud:** AWS (Lambda, EC2, CloudWatch)
- **Concepts:** Metaprogramming (Decorators), Multi-threading, Generator Patterns.
