variable "project_id" {
  description = "AceUp Demo Project"
  type        = string
}

variable "region" {
  description = "Default region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Default zone for resources"
  type        = string
  default     = "us-central1-a"
}

variable "credentials_file" {
  type        = string
  description = "Path to the service account JSON key"
  default     = "gcp_key.json"
}

variable "service_name" {
  type        = string
  description = "Name for the Cloud Run service"
  default     = "aceup-demo-ml-engineer"
}

variable "container_image" {
  type        = string
  description = "Full container image reference (Docker Hub or Artifact Registry)"
}

variable "opeanai_api_key" {
  type        = string
  description = "opeanai api key var"
}
