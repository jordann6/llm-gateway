variable "name_prefix" {
  type = string
}

variable "container_port" {
  type = number
}

variable "tags" {
  type = map(string)
}