document.addEventListener('DOMContentLoaded', () => {
    const audio = document.getElementById('background-music');
    audio.volume = 0.1;
    const muteButton = document.getElementById('mute-button');
    const playMusicPrompt = document.getElementById('play-music-prompt');
    const playMusicButton = document.getElementById('play-music-button');
    const clickSound = new Audio(window.clickSoundUrl);
    clickSound.volume = 0.3;

    const playClickSound = () => {
        if (!audio.muted) {
            clickSound.currentTime = 0;
            clickSound.play().catch(() => {});
        }
    };

    document.querySelectorAll('button, a').forEach(element => {
        element.addEventListener('click', playClickSound);
    });

    const updateMuteButtonText = () => {
        muteButton.textContent = audio.muted ? 'Unmute' : 'Mute';
    };

    const savedTime = sessionStorage.getItem('audioTime');
    const isMuted = sessionStorage.getItem('audioMuted') === 'true';
    if (savedTime) audio.currentTime = parseFloat(savedTime);
    audio.muted = isMuted;
    updateMuteButtonText();

    const playAudio = () => {
        audio.play().then(() => {
            if (playMusicPrompt) playMusicPrompt.style.display = 'none';
        }).catch(() => {
            if (playMusicPrompt) {
                playMusicPrompt.style.display = 'block';
            } else {
                document.addEventListener('click', () => audio.play().catch(() => {}), { once: true });
            }
        });
    };

    playAudio();

    if (playMusicButton) {
        playMusicButton.addEventListener('click', () => {
            audio.play().then(() => {
                playMusicPrompt.style.display = 'none';
            }).catch(() => {});
        });
    }

    window.addEventListener('beforeunload', () => {
        sessionStorage.setItem('audioTime', audio.currentTime);
        sessionStorage.setItem('audioMuted', audio.muted);
    });

    muteButton.addEventListener('click', () => {
        audio.muted = !audio.muted;
        updateMuteButtonText();
        sessionStorage.setItem('audioMuted', audio.muted);
    });
});