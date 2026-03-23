variable "project_id" {
  description = "GCP project ID"
  type = string
}

variable "service_account_id" {
  description = "Service account for invoking cloud run"
  type = string
}

variable "image_tag" {
  description = "Container image tag (e.g. short commit SHA)"
  type        = string
}