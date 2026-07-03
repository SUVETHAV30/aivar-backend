terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # For a production setup, it's recommended to store state in an S3 bucket
  # backend "s3" {
  #   bucket         = "aivar-terraform-state"
  #   key            = "state/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "aivar-terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AIVAR-Baseline"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
