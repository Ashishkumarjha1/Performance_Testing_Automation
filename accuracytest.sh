#!/bin/bash

# Prompt the user for input
read -p "Enter IP address: " ip_address
read -p "Enter port: " port
read -p "Enter username: " username
read -sp "Enter password: " password
echo
read -p "Enter description: " description
read -p "Enter test run name: " test_run_name
read -p "Enter software version: " software_version
read -p "Enter tester name: " tester_name
read -p "Enter test suit name: " test_suit_name

# Create the JSON file with the provided details
cat <<EOF > login_details.json
{
    "ip_address": "$ip_address",
    "port": "$port",
    "username": "$username",
    "password": "$password",
    "description": "$description",
    "test_run_name": "$test_run_name",
    "software_version": "$software_version",
    "tester_name": "$tester_name",
    "test_suit_name": "$test_suit_name"
}
EOF

echo "Login details saved to login_details.json"
python3 main_script.py
