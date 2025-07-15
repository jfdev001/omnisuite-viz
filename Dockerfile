# @brief Sets up docker development environment for omnisuite-viz
# 
# @todo
# * Could git clone the source code instead
FROM python:3.12-slim
SHELL ["/bin/bash", "-c"] 

# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcdf-bin \
    eog \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /omnisuite-viz 

# Copy repo files
COPY . .

# Install Python requirements and scientific packages
RUN pip install -r requirements.txt 
RUN pip install -e . 

CMD ["bash"]
