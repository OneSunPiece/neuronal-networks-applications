# Use AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.11


# Copy application code and dependencies
COPY main.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT}
#RUN pip install --no-cache-dir tensorflow numpy

# Set the CMD to your function handler
CMD ["main.lambda_handler"]
