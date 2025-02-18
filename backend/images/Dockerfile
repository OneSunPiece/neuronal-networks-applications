# Use AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11

# File with dependencies
COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# Copy application code
COPY main.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your function handler
CMD ["main.lambda_handler"]
