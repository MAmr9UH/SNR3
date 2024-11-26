import os
import math
import subprocess
from flask import Flask, request, jsonify
import requests

# Install dependencies if not already installed
def install_dependencies():
    try:
        print("Installing dependencies...")
        subprocess.check_call(['pip3', 'install', '--upgrade', 'pip'])
        subprocess.check_call(['pip3', 'install', 'flask'])
        subprocess.check_call(['pip3', 'install', 'requests'])
    except FileNotFoundError:
        print("pip3 not found. Make sure pip3 is installed.")
        exit(1)
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        exit(1)

install_dependencies()

# Initialize Flask app
app = Flask(__name__)

# Azure SignalR Service details
SIGNALR_ENDPOINT = "https://snr90.service.signalr.net"  # Your SignalR service endpoint
SIGNALR_KEY = "CiGls0Lfg7olcRj26L2gaS6QFJMlbTQfPaGeJdczGfjz414qiOTFJQQJ99AKACYeBjFXJ3w3AAAAASRSmw9Y"  # Your SignalR primary key
HUB_NAME = "chatHub"  # Your SignalR hub name

# Function to calculate Signal-to-Noise Ratio (SNR)
def calculate_snr(signal, noise):
    if noise == 0:
        return float('inf')  # Infinite SNR if there's no noise
    return 10 * math.log10(signal / noise)

# API endpoint to handle messages
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Calculate SNR
    signal = len(message)
    noise = 1  # Simulated noise value
    snr = calculate_snr(signal, noise)

    # Send message and SNR to Azure SignalR Service
    url = f"{SIGNALR_ENDPOINT}/api/v1/hubs/{HUB_NAME}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SIGNALR_KEY}"
    }
    payload = {"target": "ReceiveMessage", "arguments": [message, snr]}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return jsonify({"message": message, "SNR": snr}), 200
    else:
        return jsonify({"error": "Failed to send message", "details": response.text}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
