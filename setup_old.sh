#!/bin/bash

# Add new user
sudo adduser nadooit
sudo usermod -aG sudo nadooit

# Install required packages
sudo apt-get update
sudo apt-get install -y git curl apt-transport-https ca-certificates gnupg-agent software-properties-common

# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone the repository
git clone git@github.com:NADOOIT/NADOO-IT.git

# Change to the project directory
cd NADOO-IT

# Copy the .env.example file to .env
cp .env.example .env

# Enable memory overcommit
if ! grep -q "vm.overcommit_memory = 1" /etc/sysctl.conf; then
  echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
fi

# Apply the changes without rebooting
sudo sysctl -p

echo "Server setup complete."

echo "Do you want to add the info for the .env file now? (y/n)"
read answer
if [ "$answer" = "y" ]; then
  read -p "DJANGO_SECRET_KEY: " django_secret_key
  read -p "DOMAIN (for DJANGO_CSRF_TRUSTED_ORIGINS): " domain
  read -p "ACME_DEFAULT_EMAIL: " acme_default_email
  read -p "COCKROACH_DB_HOST: " cockroach_db_host
  read -p "COCKROACH_DB_NAME: " cockroach_db_name
  read -p "COCKROACH_DB_PORT: " cockroach_db_port
  read -p "COCKROACH_DB_USER: " cockroach_db_user
  read -p "COCKROACH_DB_PASSWORD: " cockroach_db_password
  read -p "COCKROACH_DB_OPTIONS: " cockroach_db_options
  read -p "NADOOIT__API_KEY: " nadooit_api_key
  read -p "NADOOIT__USER_CODE: " nadooit_user_code

  sed -i "s/your_secret_key/$django_secret_key/" .env
  sed -i "s/your_domain/$domain/" .env
  sed -i "s/your_email/$acme_default_email/" .env
  sed -i "s/your_cockroach_db_host/$cockroach_db_host/" .env
  sed -i "s/your_cockroach_db_name/$cockroach_db_name/" .env
  sed -i "s/your_cockroach_db_port/$cockroach_db_port/" .env
  sed -i "s/your_cockroach_db_user/$cockroach_db_user/" .env
  sed -i "s/your_cockroach_db_password/$cockroach_db_password/" .env
  sed -i "s/your_cockroach_db_options/$cockroach_db_options/" .env
  sed -i "s/your_nadooit_api_key/$nadooit_api_key/" .env
  sed -i "s/your_nadooit_user_code/$nadooit_user_code/" .env
  sed -i "s/DJANGO_DEBUG=1/DJANGO_DEBUG=0/" .env
  
  echo "Building the Docker images..."
  docker-compose -f docker-compose.deploy.yml build
  docker-compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh

  echo "Running migrations..."
  docker-compose -f docker-compose.deploy.yml run --rm app python manage.py migrate

  echo "Creating superuser..."
  docker-compose -f docker-compose.deploy.yml run --rm app python manage.py createsuperuser

  echo "Starting the server..."
  docker-compose -f docker-compose.deploy.yml up -d
fi

echo "The .env file has been updated with the provided information."
echo "If you chose not to update the .env file, follow the setup instructions in the documentation."