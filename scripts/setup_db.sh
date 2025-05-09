#!/bin/bash

# Create config directory if it doesn't exist
mkdir -p config

# Check if config file already exists
if [ -f "config/db_seed.yaml" ]; then
  echo "Config file already exists at config/db_seed.yaml"
  echo "To create a new one, please rename or delete the existing file"
  exit 1
fi

# Create sample config file
cat > config/db_seed.yaml << 'EOL'
# Database Seed Configuration

# Database connection (all fields are optional and will use defaults if not specified)
database:
  host: localhost
  port: 5432
  name: health_dashboard
  user: username
  password: password
  # Alternatively, you can specify a complete connection string:
  # url: postgresql://username:password@localhost:5432/health_dashboard

# Admin users
admins:
  - username: admin
    password: admin_password
  - username: supervisor
    password: super_password

# Groups
groups:
  - name: Group A
    description: Test group for team A
    created_by: admin  # Optional - defaults to first admin if not specified
  - name: Group B 
    description: Test group for team B
    created_by: supervisor
  - name: Group C
    description: Test group for team C

# Participants
participants:
  - username: participant1
    password: participant1_password
    groups: Group A
    generate_data: true  # Optional - defaults to true
    data_days: 60  # Optional - how many days of mock data to generate, defaults to 60
  
  - username: participant2
    password: participant2_password
    groups: Group A
    
  - username: participant3
    password: participant3_password
    groups: [Group A, Group B]  # Can assign to multiple groups
    
  - username: participant4
    password: participant4_password
    groups: Group B
    data_days: 30  # Generate only 30 days of data
    
  - username: participant5
    password: participant5_password
    groups: Group C
    
  - username: participant6
    password: participant6_password
    groups: Group C
    generate_data: false  # Don't generate mock health data
EOL

echo "Sample configuration created at config/db_seed.yaml"
echo "Please edit this file with your desired users, groups, and passwords"
echo "Then run: python scripts/init_db.py --drop --seed --config config/db_seed.yaml"