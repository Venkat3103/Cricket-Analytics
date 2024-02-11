provider "aws" {
  region = "us-east-1"
}


# Create iam role for lambda function


resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda-exec-role"

  assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Sid    = ""
                Principal = {
                    Service = "lambda.amazonaws.com"
                }
            }
        ]
    })
}


# Attach s3 access policy to lambda 
resource "aws_iam_role_policy_attachment" "lambda_exec_role_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}


# Creating a S3 bucket
resource "aws_s3_bucket" "ball_by_ball_data" {
  bucket = "ball-by-ball-data"
}


# Zipping the lambda function

data "archive_file" "lambda_function_payload" {
  type        = "zip"
  source_dir  = "../lambda_function"
  output_path = "${path.module}/lambda_function.zip"
}

# Creating the lambda function

resource "aws_lambda_function" "process_ball_by_ball_data" {
  filename      = data.archive_file.lambda_function_payload.output_path
  function_name = "process-ball-by-ball-data"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.8"
  timeout       = 900
}


# Event rule to trigger lambda function
resource "aws_cloudwatch_event_rule" "trigger_lambda" {
  name                = "trigger-lambda-every-5-mins"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.trigger_lambda.name
  target_id = "trigger-lambda-function"
  arn       = aws_lambda_function.process_ball_by_ball_data.arn
}


resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_ball_by_ball_data.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.trigger_lambda.arn
}

