variable "project_name" {
  type = "string"
}

variable "environment" {
  type = "string"
}

variable "vpc_cidr_block" {
  type = "string"
}

variable "private_subnet_cidr_blocks" {
  type = "list"
}

variable "public_subnet_cidr_blocks" {
  type = "list"
}
