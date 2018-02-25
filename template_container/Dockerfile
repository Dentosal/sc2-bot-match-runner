# Use an official Python runtime as a parent image
FROM ubuntu:17.10

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install needed packages
RUN apt update -y
RUN apt-get install -y python3-pip strace
RUN pip3 install --trusted-host pypi.python.org sc2

# Create users
RUN useradd -ms /bin/bash user0
RUN useradd -ms /bin/bash user1

RUN ln -s /StarCraftII /home/user0/StarCraftII
RUN ln -s /StarCraftII /home/user1/StarCraftII

RUN chown -R user0 /app/repo0
RUN chown -R user1 /app/repo1

RUN chmod -R 700 /app/repo0
RUN chmod -R 700 /app/repo1

RUN ln -s /app/repo0 /home/user0/repo
RUN ln -s /app/repo1 /home/user1/repo

# Run startup.py when the container launches
# Hack: chown to ensure the bots have access to their respective output dirs. Without this,
# the both dirs will be owned by user0 when running under Ubuntu
CMD chown user0 /result0 && chown user1 /result1 && python3 startup.py
