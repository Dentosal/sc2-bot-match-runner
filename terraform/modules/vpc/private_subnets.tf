resource "aws_subnet" "private" {
  count             = "${length(var.private_subnet_cidr_blocks)}"
  vpc_id            = "${aws_vpc.main.id}"
  cidr_block        = "${var.private_subnet_cidr_blocks[count.index]}"
  availability_zone = "${data.aws_availability_zones.available.names[count.index]}"

  tags {
    Name        = "${var.project_name}-private-subnet-${count.index + 1}"
    Project     = "${var.project_name}"
    Environment = "${var.environment}"
  }
}

resource "aws_route_table" "private" {
  count  = "${length(var.private_subnet_cidr_blocks)}"
  vpc_id = "${aws_vpc.main.id}"

  tags {
    Name        = "${var.project_name}-private-route-table-${count.index + 1}"
    Project     = "${var.project_name}"
    Environment = "${var.environment}"
  }
}

resource "aws_route" "private_to_nat" {
  count          = "${length(var.private_subnet_cidr_blocks)}"
  route_table_id = "${element(aws_route_table.private.*.id, count.index)}"

  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = "${element(aws_nat_gateway.main.*.id, count.index)}"
}

resource "aws_route_table_association" "private" {
  count          = "${length(var.private_subnet_cidr_blocks)}"
  route_table_id = "${element(aws_route_table.private.*.id, count.index)}"
  subnet_id      = "${element(aws_subnet.private.*.id, count.index)}"
}
