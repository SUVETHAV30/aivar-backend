variable "aws_region" {
  description = "The AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_password" {
  description = "PostgreSQL Database Admin Password"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "PostgreSQL Database Admin Username"
  type        = string
  default     = "aivar_admin"
}

variable "backend_image" {
  description = "Docker image URI for the backend service"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API Key for the backend"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT Secret Key for auth"
  type        = string
  sensitive   = true
}
