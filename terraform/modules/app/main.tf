resource "aws_security_group" "app_lb" {
  name_prefix = "${var.app_name}"
  description = "${var.app_name} load balancer network rules"
  vpc_id      = "${var.vpc_id}"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "app" {
  name_prefix = "${var.app_name}"
  description = "${var.app_name} application network rules"
  vpc_id      = "${var.vpc_id}"

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = ["${aws_security_group.app_lb.id}"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "runner" {
  ami             = "${var.image_id}"
  instance_type   = "${var.instance_type}"
  key_name        = "${var.ssh_key_name}"
  vpc_security_group_ids = ["${aws_security_group.app.id}"]
  subnet_id       = "${element(var.lb_subnets, 0)}"
  associate_public_ip_address = true
  root_block_device {
    volume_size    = "16"
  }
  tags {
    Name = "${var.app_name}"
    Environment = "${var.environment}"
  }
}

resource "aws_lb" "app" {
  internal           = false
  load_balancer_type = "application"
  security_groups    = ["${aws_security_group.app_lb.id}"]
  subnets            = ["${var.lb_subnets}"]

  tags {
    Name        = "${var.app_name}-lb"
    Project     = "${var.project_name}"
    Environment = "${var.environment}"
  }
}

resource "aws_lb_target_group" "app" {
  port     = "${var.app_port}"
  protocol = "${var.app_protocol}"
  vpc_id   = "${var.vpc_id}"
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = "${aws_lb.app.arn}"
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = "${aws_lb_target_group.app.arn}"
    type             = "forward"
  }
}
