# Handify - Gesture-controlled Spotify player.
# Copyright (C) 2024 Christopher Muntean
#
# This file is part of Handify and is licensed under the
# GNU General Public License v3.0. For details, see <https://www.gnu.org/licenses/>.

# Use Python 3.10 slim image as the base
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Command to run the app using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "handify:handify"]