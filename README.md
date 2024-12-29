<div align="center">

# Handify | [Docker Hub](https://hub.docker.com/r/chrismuntean/handify)

### Gesture-controlled Spotify player. Built using Google MediaPipe Hand Landmarker and the Spotify Web API.

![GitHub commit activity](https://img.shields.io/github/commit-activity/t/chrismuntean/handify)
![Docker Pulls](https://img.shields.io/docker/pulls/chrismuntean/handify.svg)
![GitHub License](https://img.shields.io/github/license/chrismuntean/handify)
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
![Docker Image Size](https://img.shields.io/docker/image-size/chrismuntean/handify)


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
        <h3><b>Volume control</b></h3>
        Adjust the volume by pinching your index and thumb after making the love sign in ASL.
    </td>
  </tr>

</table>
<br>

## Demonstration
<br>

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).

By using, modifying, or distributing this software, you agree to the terms and conditions set forth in the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). In summary:

- You are free to use, modify, and distribute this software, provided that any derivative works are also licensed under the GNU GPL v3.0.
- Any distributed copies or modifications must include this license and provide access to the source code.
- There is no warranty for this software. It is provided "as-is" without any guarantees of performance or suitability for a particular purpose.

For more details, refer to the full [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

### Contributing
If you wish to contribute to this project, your help is welcome! Contributions can include reporting bugs, suggesting new features, improving documentation, or submitting code enhancements.

By contributing to this project, you agree to license your contributions under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). This ensures that the project remains open source and free for everyone to use, modify, and distribute.

**To contribute:**
1. Fork the repository to your own GitHub account.
2. Create a new branch for your changes: `git checkout -b my-feature-branch`.
3. Commit your changes: `git commit -m "Add some feature"`.
4. Push to your fork: `git push origin my-feature-branch`.
5. Open a pull request against the main branch of this repository.

*Please make sure your contributions:*
- Follow the coding style and conventions used in the project.
- Include documentation or comments for any new features or changes.
- Are tested (if applicable) to ensure functionality.

If you’re unsure about your contribution or have any questions, feel free to reach out to me at [hello@chrismuntean.dev](mailto:hello@chrismuntean.dev).

Thank you for helping make this project better!

<br>

## Acknowledgments
```
@misc{google2024mediapipe,
  title = {Mediapipe: Cross-platform machine learning solutions for live and streaming media},
  author = {Google AI},
  year = {2024},
  url = {https://mediapipe.dev}
}

@misc{opencv2024,
  title = {OpenCV: Open Source Computer Vision Library},
  author = {OpenCV team},
  year = {2024},
  url = {https://opencv.org/}
}

@misc{spotify2024spotipy,
  title = {Spotipy: A lightweight Python library for the Spotify Web API},
  author = {Spotify Developers},
  year = {2024},
  url = {https://spotipy.readthedocs.io/}
}
```