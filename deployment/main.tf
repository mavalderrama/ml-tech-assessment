
resource "google_cloud_run_v2_service" "app" {
  name     = var.service_name
  location = var.region

  deletion_protection = false

  template {
    timeout = "300s"
    containers {
      image = var.container_image
      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.openai_api_key.id
            version = "1"
          }
        }
      }
      startup_probe {
        # initial_delay_seconds = 240
        timeout_seconds   = 100
        period_seconds    = 3
        failure_threshold = 1
        tcp_socket {
          port = 8000
        }
      }
      liveness_probe {
        http_get {
          path = "/"
        }
      }

      ports {
        container_port = 8000
      }
    }

    # small CPU/RAM to stay well inside free
    scaling {
      min_instance_count = 0
      max_instance_count = 1
    }
  }
  ingress = "INGRESS_TRAFFIC_ALL"
}

resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "OPENAI_API_KEY"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "openai_api_key_v1" {
  secret      = google_secret_manager_secret.openai_api_key.id
  secret_data = var.opeanai_api_key
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  name     = google_cloud_run_v2_service.app.name
  location = google_cloud_run_v2_service.app.location
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}
