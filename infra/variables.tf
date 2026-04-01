variable "railway_token" {
  description = "Railway API token — set via TF_VAR_railway_token env var"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Django SECRET_KEY"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}
