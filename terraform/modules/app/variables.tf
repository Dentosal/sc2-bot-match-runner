variable "app_name" {
  type = "string"
}

variable "project_name" {
  type = "string"
}

variable "environment" {
  type = "string"
}

variable "desired_capacity" {}

variable "image_id" {
  type = "string"
}

variable "instance_type" {
  type = "string"
}

variable "ssh_key_name" {
  type = "string"
}

variable "vpc_id" {
  type = "string"
}

variable "app_subnets" {
  type = "list"
}

variable "lb_subnets" {
  type = "list"
}

variable "app_port" {}

variable "app_protocol" {
  type = "string"
}
