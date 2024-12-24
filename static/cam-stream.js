document.addEventListener("DOMContentLoaded", () => {
    const userId = document.getElementById('user-id').value; // Hidden element for User ID
    const video = document.querySelector("#videoPreview"); // Video element for webcam preview
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;

            // Wait until the video stream starts
            video.onloadedmetadata = () => {
                // Set canvas dimensions to match video dimensions
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                // Start sending frames to the backend
                const sendFrame = () => {
                    // Draw video frame to canvas
                    try {
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        canvas.toBlob(blob => {
                            if (blob) {
                                fetch('/upload_frame', {
                                    method: 'POST',
                                    body: blob,
                                    headers: {
                                        'Content-Type': 'image/jpeg',
                                        'User-ID': userId
                                    }
                                }).catch(err => console.error("[ERROR] Issue sending frame:", err));
                            }
                        }, 'image/jpeg');
                    } catch (err) {
                        console.error("[ERROR] Issue processing frame:", err);
                    }
                };

                // Send frames at a throttled interval
                setInterval(sendFrame, 200); // Adjust interval (200ms = 5fps)
            };
        })
        .catch(error => console.error("[ERROR] Webcam access denied:", error));
});