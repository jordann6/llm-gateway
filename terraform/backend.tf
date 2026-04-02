terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket = "tf-backend-jord-projs"
    key    = "llm-gateway/terraform.tfstate"
    region = "us-east-1"
  }
}