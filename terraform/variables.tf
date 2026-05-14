variable "aws_region" {
  description = "AWS region to deploy Lambda"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "Must be a valid AWS region format e.g. us-east-1."
  }
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "serverless-cost-sentinel"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "project_name must be lowercase letters, numbers, and hyphens only."
  }
}

variable "tag_key" {
  description = "EC2 tag key to filter instances for shutdown"
  type        = string
  default     = "Environment"
}

variable "tag_value" {
  description = "EC2 tag value to filter instances for shutdown"
  type        = string
  default     = "Dev"
}

variable "sns_topic_name" {
  description = "Name of the SNS topic for cost sentinel alerts"
  type        = string
  default     = "cost-sentinel-alerts"
}

variable "alert_email" {
  description = "Email address to receive SNS alerts (subscription must be confirmed via email)"
  type        = string
  sensitive   = true
}

variable "report_bucket_name" {
  description = "Globally unique S3 bucket name for storing JSON summary reports"
  type        = string
}