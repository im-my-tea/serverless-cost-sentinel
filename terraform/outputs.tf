output "lambda_function_arn" {
  description = "ARN of the deployed Lambda function"
  value       = aws_lambda_function.cost_sentinel.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.cost_sentinel.function_name
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge schedule rule"
  value       = aws_cloudwatch_event_rule.daily_trigger.arn
}

output "iam_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}