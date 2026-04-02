variable "name_prefix" {
  type = string
}

variable "openai_api_key" {
  type      = string
  sensitive = true
}

variable "anthropic_api_key" {
  type      = string
  sensitive = true
}

variable "tags" {
  type = map(string)
}