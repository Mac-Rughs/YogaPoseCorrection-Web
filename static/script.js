document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed');

    const tutorialVideo = document.getElementById('tutorial-video');
    
    // Autoplay the tutorial video when it's ready
    tutorialVideo.addEventListener('canplay', () => {
        tutorialVideo.play().catch(error => {
            console.log("Autoplay was prevented:", error);
        });
    });

    // Loop the tutorial video
    tutorialVideo.addEventListener('ended', () => {
        tutorialVideo.currentTime = 0;
        tutorialVideo.play().catch(error => {
            console.log("Replay was prevented:", error);
        });
    });
});