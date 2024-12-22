function fetchCurrentSong() {
    fetch('/current-song-request')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
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

setInterval(fetchCurrentSong, 1000);  // Refresh every second