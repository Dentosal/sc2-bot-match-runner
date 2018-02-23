resource "aws_subnet" "public" {
  count             = "${length(var.public_subnet_cidr_blocks)}"
  vpc_id            = "${aws_vpc.main.id}"
  cidr_block        = "${var.public_subnet_cidr_blocks[count.index]}"
  availability_zone = "${data.aws_availability_zones.available.names[count.index]}"

  tags {
    Name        = "${var.project_name}-public-subnet-${count.index + 1}"
    Project     = "${var.project_name}"
    Environment = "${var.environment}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = "${aws_vpc.main.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.main.id}"
  }

  tags {
    Name        = "${var.project_name}-public-route-table"
    Project     = "${var.project_name}"
    Environment = "${var.environment}"
  }
}

resource "aws_route_table_association" "public" {
  count          = "${length(var.public_subnet_cidr_blocks)}"
  route_table_id = "${aws_route_table.public.id}"
  subnet_id      = "${element(aws_subnet.public.*.id, count.index)}"
}

resource "aws_eip" "nat_gateway_ip" {
  count = "${length(var.public_subnet_cidr_blocks)}"
  vpc   = true
}

resource "aws_nat_gateway" "main" {
  count         = "${length(var.public_subnet_cidr_blocks)}"
  subnet_id     = "${element(aws_subnet.public.*.id, count.index)}"
  allocation_id = "${element(aws_eip.nat_gateway_ip.*.id, count.index)}"

  tags {
    Name        = "${var.project_name}-nat-gateway-${count.index + 1}"
    Project     = "${var.project_name}"
    Environment = "${var.environment}"
  }
}
