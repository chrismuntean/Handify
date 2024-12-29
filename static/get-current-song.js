/*
Handify - Gesture-controlled Spotify player.
Copyright (C) 2024 Christopher Muntean

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

function fetchCurrentSong() {
    // Dynamically check Spotify connection and playback conditions
    const spotifyConnected = document.body.dataset.spotifyConnected === 'true';
    const playerOpened = document.body.dataset.playerOpened === 'true';
    const volumeControlSupported = document.body.dataset.volumeControlSupported === 'true';

    if (spotifyConnected && playerOpened && volumeControlSupported) {
        // Spotify is ready, proceed with fetching the current song
        fetch('/current-song-request')
            .then(response => {
                if (!response.ok) {
                    console.error('[ERROR] Issue fetching song data:', response.statusText);
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data && !data.error) {
                    document.getElementById('album-cover').src = data.album_image;
                    document.getElementById('song-name').textContent = data.song_name;
                    document.getElementById('artist-name').textContent = data.artist_name;

                    const progressPercent = (data.progress_ms / data.duration_ms) * 100;
                    document.getElementById('progress-bar').style.width = `${progressPercent}%`;

                    const elapsed = new Date(data.progress_ms).toISOString().slice(14, 19);
                    const remaining = new Date(data.duration_ms - data.progress_ms).toISOString().slice(14, 19);
                    document.getElementById('elapsed-time').textContent = elapsed;
                    document.getElementById('remaining-time').textContent = `-${remaining}`;
                }
            })
            .catch(console.error);
    }
}

// Call fetchCurrentSong periodically
setInterval(fetchCurrentSong, 1000);