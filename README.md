# Robotics Team 11 Final Project
## AI Art Attendant

This repository includes the code to run the automatic AI art attendant with a Scout Mini robot.

# Usage

API keys for for Google Gemini, ngrok, and Microsoft Azure have to be placed in a .env file to run the code.

We recommend uploading `collab_llava_host.ipynb` to a Google Colab instance and running it in a T4 GPU environment for best performence.

To run the robot ROS 2 has to be installed. First run the first two cells of `collab_llava_host.ipynb` to setup the LLaVA-Onevision host and ngrok tunnel.
Afterwards `send_to_server.py` to run the AI art attendant. The url for the ngrok tunnel generated in the colab notebook has to be passed through the standard input.
Further parameters are explained with `--help`.
