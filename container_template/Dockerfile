# Use an official Python runtime as a parent image
FROM ubuntu:17.10

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install needed packages
RUN apt update -y
RUN apt-get install -y python3-pip
# RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
RUN pip3 install -e python-sc2

# Create users
RUN useradd -ms /bin/bash user0
RUN useradd -ms /bin/bash user1

USER user$INDEX
# RUN ln -s /app/StarCraftII ~/StarCraftII
RUN ln -s /StarCraftII ~/StarCraftII

# Run app.py when the container launches
CMD $RUNCMD
