resource "aws_vpc" "main" {
  cidr_block = "${var.vpc_cidr_block}"

  tags {
    Name    = "${var.project_name}-vpc"
    Project = "${var.project_name}"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = "${aws_vpc.main.id}"

  tags {
    Name = "${var.project_name}-internet-gateway"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}
