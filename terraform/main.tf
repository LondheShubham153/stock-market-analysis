# Root Terraform Configuration
# Stock Market Analytics Dashboard - AWS Infrastructure

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS Provider Configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "stock-market-dashboard"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Local variables for resource naming
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Data source for available availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# ========================================
# Secrets Manager
# ========================================

# Secret for Alpha Vantage API Key
resource "aws_secretsmanager_secret" "api_key" {
  name        = "${local.name_prefix}/api-key${var.secret_suffix != "" ? "-" : ""}${var.secret_suffix}"
  description = "Alpha Vantage API key for stock market data"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "api_key" {
  secret_id     = aws_secretsmanager_secret.api_key.id
  secret_string = var.alpha_vantage_api_key
}

# Secret for GitHub Token
resource "aws_secretsmanager_secret" "github_token" {
  name        = "${local.name_prefix}/github-token${var.secret_suffix != "" ? "-" : ""}${var.secret_suffix}"
  description = "GitHub personal access token for CodePipeline"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "github_token" {
  secret_id     = aws_secretsmanager_secret.github_token.id
  secret_string = var.github_token
}


# ========================================
# VPC Module
# ========================================

module "vpc" {
  source = "./modules/vpc"

  name_prefix        = local.name_prefix
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway

  tags = local.common_tags
}

# ========================================
# ECR Module
# ========================================

module "ecr" {
  source = "./modules/ecr"

  repository_name         = local.name_prefix
  image_retention_count   = var.ecr_image_retention_count
  scan_on_push            = true
  image_tag_mutability    = "MUTABLE"

  tags = local.common_tags
}

# ========================================
# ALB Module
# ========================================

module "alb" {
  source = "./modules/alb"

  name_prefix        = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  container_port     = var.ecs_container_port

  health_check_path               = var.alb_health_check_path
  health_check_interval           = var.alb_health_check_interval
  health_check_timeout            = var.alb_health_check_timeout
  health_check_healthy_threshold  = var.alb_healthy_threshold
  health_check_unhealthy_threshold = var.alb_unhealthy_threshold

  tags = local.common_tags
}

# ========================================
# IAM Module
# ========================================

module "iam" {
  source = "./modules/iam"

  name_prefix = local.name_prefix

  secrets_arns = [
    aws_secretsmanager_secret.api_key.arn,
    aws_secretsmanager_secret.github_token.arn
  ]

  # Pass the expected artifacts bucket ARN (created by the codepipeline module)
  # Constructing the ARN here avoids a module ordering issue while allowing
  # the IAM role to receive the correct S3 permissions for CodePipeline.
  artifacts_bucket_arn   = "arn:aws:s3:::${local.name_prefix}-pipeline-artifacts"
  
  # Pass constructed CodeBuild project ARN so the CodePipeline role can
  # call codebuild:StartBuild without creating a module dependency cycle.
  codebuild_project_arn = "arn:aws:codebuild:${var.aws_region}:${data.aws_caller_identity.current.account_id}:project/${local.name_prefix}-build"

  tags = local.common_tags

}

# ========================================
# ECS Module
# ========================================

module "ecs" {
  source = "./modules/ecs"

  name_prefix           = local.name_prefix
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  alb_security_group_id = module.alb.alb_security_group_id
  target_group_arn      = module.alb.target_group_arn
  alb_listener_arn      = module.alb.http_listener_arn

  container_name = var.project_name
  container_port = var.ecs_container_port
  task_cpu       = var.ecs_task_cpu
  task_memory    = var.ecs_task_memory
  desired_count  = var.ecs_desired_count

  task_execution_role_arn = module.iam.ecs_task_execution_role_arn
  task_role_arn           = module.iam.ecs_task_role_arn

  ecr_repository_url = module.ecr.repository_url

  # Inject API key from Secrets Manager
  secrets = [
    {
      name       = "ALPHA_VANTAGE_API_KEY"
      value_from = aws_secretsmanager_secret.api_key.arn
    }
  ]

  log_retention_days        = var.log_retention_days
  enable_container_insights = var.enable_container_insights
  aws_region                = var.aws_region

  tags = local.common_tags

  depends_on = [module.alb]
}

# ========================================
# CodeBuild Module
# ========================================

module "codebuild" {
  source = "./modules/codebuild"

  project_name      = "${local.name_prefix}-build"
  service_role_arn  = module.iam.codebuild_role_arn
  compute_type      = var.codebuild_compute_type
  image             = var.codebuild_image

  ecr_registry_url    = split("/", module.ecr.repository_url)[0]
  ecr_repository_name = module.ecr.repository_name
  aws_region          = var.aws_region

  log_retention_days = 30

  tags = local.common_tags

  depends_on = [module.ecr, module.iam]
}

# ========================================
# CodePipeline Module
# ========================================

module "codepipeline" {
  source = "./modules/codepipeline"

  name_prefix  = local.name_prefix
  pipeline_name = "${local.name_prefix}-pipeline"

  service_role_arn = module.iam.codepipeline_role_arn

  github_owner  = var.github_owner
  github_repo   = var.github_repo
  github_branch = var.github_branch
  github_token  = var.github_token

  codebuild_project_name = module.codebuild.project_name

  ecs_cluster_name = module.ecs.cluster_name
  ecs_service_name = module.ecs.service_name

  notification_email = var.notification_email

  tags = local.common_tags

  depends_on = [module.codebuild, module.ecs, module.iam]
}

# ========================================
# Monitoring Module
# ========================================

module "monitoring" {
  source = "./modules/monitoring"

  name_prefix = local.name_prefix

  sns_topic_arn = module.codepipeline.sns_topic_arn

  ecs_cluster_name    = module.ecs.cluster_name
  ecs_service_name    = module.ecs.service_name
  desired_task_count  = var.ecs_desired_count

  # Extract ARN suffixes for CloudWatch metrics
  alb_arn_suffix         = split(":", module.alb.alb_arn)[5]
  target_group_arn_suffix = split(":", module.alb.target_group_arn)[5]

  pipeline_name          = module.codepipeline.pipeline_name
  enable_pipeline_alarms = true

  tags = local.common_tags

  depends_on = [module.ecs, module.alb, module.codepipeline]
}
