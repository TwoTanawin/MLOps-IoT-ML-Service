#!/bin/bash
# Update system and install Docker
apt-get update -y
apt-get install -y docker.io curl

# Enable Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose v2
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create working directory
mkdir -p /opt/mlops_ml_db && cd /opt/mlops_ml_db

# Write docker-compose.yml with restart policy
cat <<EOF > docker-compose.yml
services:
  mlops_ml_svc:
    image: postgres:16
    container_name: ml_db
    platform: linux/amd64
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ml_db
    ports:
      - "5435:5432"
    restart: always
    networks:
      - mlops_network

networks:
  mlops_network:
    driver: bridge
EOF

# Create systemd service to run Docker Compose on boot
cat <<EOF > /etc/systemd/system/mlops_ml_db.service
[Unit]
Description=MLOps PostgreSQL Docker Compose Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/opt/mlops_ml_db
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable our service
systemctl daemon-reload
systemctl enable mlops_ml_db
systemctl start mlops_ml_db

# Optional: prevent instance from going idle (EC2 doesn't sleep, but just in case)
systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target