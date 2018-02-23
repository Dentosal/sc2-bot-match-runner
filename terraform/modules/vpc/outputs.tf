output "private_subnet_ids" {
  value = ["${aws_subnet.private.*.id}"]
}

output "public_subnet_ids" {
  value = ["${aws_subnet.public.*.id}"]
}

output "subnet_availability_zones" {
  value = ["${aws_subnet.private.*.availability_zone}"]
}

output "vpc_id" {
  value = "${aws_vpc.main.id}"
}
