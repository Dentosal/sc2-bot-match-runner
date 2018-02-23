# VPC Module

This module creates all the networking resources.

## Resources

- 1 VPC
- 3 public subnets (in different availability zones)
- 3 private subnets (eu-west-1a, b and c)
- 1 Internet Gateway for the whole VPC (for outside internet access)
- 1 NAT Gateway in a public subnet
- 1 Elastic IP for the NAT Gateway
- 1 route table for private subnets
- 1 route table for public subnets