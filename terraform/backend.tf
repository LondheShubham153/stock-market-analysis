# Terraform Backend Configuration
# This configures remote state storage in S3 with DynamoDB for state locking
# Backend must be initialized after S3 bucket and DynamoDB table are created

terraform {
  backend "s3" {
    bucket         = "stock-dashboard-terraform-state3"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    
    # Uncomment after initial backend setup
    # kms_key_id = "alias/terraform-state"
  }
}
