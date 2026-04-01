terraform {
  required_providers {
    railway = {
      source  = "terraform-community-providers/railway"
      version = "~> 0.3"
    }
  }
}

provider "railway" {
  token = var.railway_token
}

resource "railway_project" "monk" {
  name = "monk"
}

resource "railway_service" "backend" {
  project_id = railway_project.monk.id
  name       = "backend"
}

resource "railway_service" "frontend" {
  project_id = railway_project.monk.id
  name       = "frontend"
}
