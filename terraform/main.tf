terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.32"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# zip src/ folder
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda_package.zip"
}

# IAM Role — temp IAM user for svcs
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# IAM Policy — what the role is allowed to do
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EC2Permissions"
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeRegions",
          "ec2:StopInstances"
        ]
        Resource = "*"
      },
      {
        Sid    = "CloudWatchLogging"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# The Lambda function
resource "aws_lambda_function" "cost_sentinel" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = var.project_name
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  timeout          = 300
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TAG_KEY   = var.tag_key
      TAG_VALUE = var.tag_value
    }
  }
}

# EventBridge rule — cron schedule
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "${var.project_name}-schedule"
  description         = "Triggers cost sentinel daily at midnight UTC"
  schedule_expression = "cron(0 0 * * ? *)"
}

# EventBridge target — points the rule at Lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "CostSentinelTarget"
  arn       = aws_lambda_function.cost_sentinel.arn
}

# Permission for EventBridge to invoke Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_sentinel.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}