# @brief Sets up docker development environment for omnisuite-examples
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
    direnv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /omnisuite-examples 

# Copy repo files
COPY . .

# Setup direnv 
RUN echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
RUN cat ~/.bashrc 
RUN chmod +x ~/.bashrc
RUN . ~/.bashrc  
RUN direnv allow .
RUN echo $(which python)

# Check if repo files present...
RUN pwd
RUN ls -a
RUN echo $PATH 

# Setup virtual environment
RUN python -m .venv venv 
RUN chmod +x .venv/bin/activate  
RUN . .venv/bin/activate 

# Install Python requirements and scientific packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e . && 

CMD ["bash"]
