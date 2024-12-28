<div align="center">

# Handify | [Docker Hub](https://hub.docker.com/r/chrismuntean/handify)

### Gesture-controlled Spotify player. Built using Google MediaPipe Hand Landmarker and the Spotify Web API.

![GitHub commit activity](https://img.shields.io/github/commit-activity/t/chrismuntean/handify)
![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4%EF%B8%8F-blue)
![GitHub Release Version](https://img.shields.io/github/v/release/chrismuntean/handify)

</div>

## Installation
Begin by cloning the repository to your local machine:
```bash
git clone https://github.com/chrismuntean/Handify.git
```
<br>

### Configure environment variables
Format for `.env` file
```bash
SPOTIFY_CLIENT_ID=<YOUR_SPORTIFY_CLIENT>
SPOTIFY_CLIENT_SECRET=<YOUR_SPOTIFY_SECRET>

FLASK_SECRET_KEY=<YOUR_GENERATED_SECRET_KEY>
FLASK_HOST=http://0.0.0.0:8080
FLASK_DEBUG=True
```
**TIPS:**
* Sign up as a developer with Spotify to get a client ID and secret at [developer.spotify.com](https://developer.spotify.com)
* Generate a secure flask secret key by running: `$ python -c "import secrets; print(secrets token_hex(32))"`
* Flask host for running with Python virtual environment is http://127.0.0.1:5000 for Docker it is http://0.0.0.0:8080
* `FLASK_DEBUG` also determines to use secure/ insecure cookies (use True for local development)
<br>

### Python virtual environment installation
```bash
python3.10 -m venv .venv310
source .venv310/bin/activate
pip install -r requirements.txt
python app.py
```
**Note:** *Python version 3.10 or earlier is required* to run Google MediaPipe as of right now
<br><br>

### Docker installation
![Docker Pulls](https://img.shields.io/docker/pulls/chrismuntean/handify.svg)

Dockerfile and `docker-compose.yml` file are included in the repository.

For more details on the Docker image, visit the [Handify Docker Hub page](https://hub.docker.com/r/chrismuntean/handify).

```bash
docker compose up
```
**Note:** Your webcam must be passed correctly under `devices` in the `docker-compose.yml` file. *This may differ on your machine.*
<br><br>

## Programmed Gestures
<table>
  
  <tr>
    <td>
      <img src="/static/pinch.png" alt="Love sign in American Sign Lanugage">
    </td>
    <td>
        <h3><b>Volume control. </b></h3>
        Adjust the volume by pinching your index and thumb after making the love sign in ASL.
    </td>
  </tr>

</table>
<br>

## Demonstration
<br>

## Acknowledgments
<br>