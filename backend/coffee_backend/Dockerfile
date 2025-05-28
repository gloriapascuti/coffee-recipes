# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY backend/coffee_backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY backend/coffee_backend/ ./

# Collect static files (if any)
# aws elbv2 describe-load-balancers \
  #  --names coffee-alb \
  #  --region $AWS_REGION \
  #  --query 'LoadBalancers[0].DNSName' \
  #  --output textRUN python manage.py

# Expose port and run
EXPOSE 8000
CMD ["gunicorn", "coffee_backend.wsgi:application", "--bind", "0.0.0.0:8000"]