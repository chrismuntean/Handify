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
    } else {
        // Spotify is not ready, skip the fetch
        console.log('[INFO] Spotify is not ready for API calls.');
    }
}

// Call fetchCurrentSong periodically
setInterval(fetchCurrentSong, 1000);