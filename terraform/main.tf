# terraform/main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.34.0"
    }
  }
}

data "google_client_openid_userinfo" "me" {}


provider "google" {
  project = var.project_id
  region  = "us-central1"
}

resource "google_cloud_run_v2_service" "backend" {
  name     = "backend-api"
  location = "us-central1"
  deletion_protection = false

  template {
    containers {
      image = "gcr.io/${var.project_id}/backend:${var.image_tag}"
    }
    service_account = local.service_account_email
  }
}

resource "google_cloud_run_v2_service" "frontend" {
  name     = "frontend"
  location = "us-central1"
  deletion_protection = false

  template {
    containers {
      image = "gcr.io/${var.project_id}/frontend:${var.image_tag}"

      env {
        name  = "BACKEND_URL"
        value = google_cloud_run_v2_service.backend.uri
      }
    }
    service_account = local.service_account_email
  }
}

data "google_client_config" "current" {}

locals {
  service_account_email = "${var.service_account_id}@developer.gserviceaccount.com"
}

resource "google_cloud_run_service_iam_binding" "invokers" {
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  service  = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"

  members = [
    # N8N Service Account
    "serviceAccount:${local.service_account_email}",
    "user:${data.google_client_openid_userinfo.me.email}"
  ]
}