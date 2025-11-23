# Terraform Variables
# Stock Market Analytics Dashboard

# General Configuration
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "stock-dashboard"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

# ECS Configuration
variable "ecs_task_cpu" {
  description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)"
  type        = string
  default     = "512"
}

variable "ecs_task_memory" {
  description = "Memory for ECS task in MB (512, 1024, 2048, etc.)"
  type        = string
  default     = "1024"
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type        = number
  default     = 2
}

variable "ecs_container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8080
}

# GitHub Configuration
variable "github_owner" {
  description = "GitHub repository owner/organization"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "github_branch" {
  description = "GitHub branch to deploy from"
  type        = string
  default     = "main"
}

# Application Configuration
variable "alpha_vantage_api_key" {
  description = "Alpha Vantage API key for stock data"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub personal access token for CodePipeline"
  type        = string
  sensitive   = true
}

# Monitoring Configuration
variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights for ECS"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention in days"
  type        = number
  default     = 7
}

# Cost Optimization
variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (disable for cost savings in dev)"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway instead of one per AZ (cost savings)"
  type        = bool
  default     = false
}

# ECR Configuration
variable "ecr_image_retention_count" {
  description = "Number of images to retain in ECR"
  type        = number
  default     = 10
}

# ALB Configuration
variable "alb_health_check_path" {
  description = "Health check path for ALB target group"
  type        = string
  default     = "/"
}

variable "alb_health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "alb_health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

variable "alb_healthy_threshold" {
  description = "Number of consecutive health checks for healthy status"
  type        = number
  default     = 2
}

variable "alb_unhealthy_threshold" {
  description = "Number of consecutive health checks for unhealthy status"
  type        = number
  default     = 3
}

# CodeBuild Configuration
variable "codebuild_compute_type" {
  description = "CodeBuild compute type"
  type        = string
  default     = "BUILD_GENERAL1_SMALL"
}

variable "codebuild_image" {
  description = "CodeBuild Docker image"
  type        = string
  default     = "aws/codebuild/standard:7.0"
}

# Notification Configuration
variable "notification_email" {
  description = "Email address for pipeline notifications"
  type        = string
  default     = ""
}

# Optional suffix appended to secret names to avoid conflicts with secrets
# that are scheduled for deletion (useful when you don't want to restore).
variable "secret_suffix" {
  description = "Optional suffix appended to Secrets Manager secret names"
  type        = string
  default     = ""
}
