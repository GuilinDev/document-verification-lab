# Rebuild the walkthrough

The committed voice, word timings, source images, Inter font (OFL) and compositions are enough to rebuild a narrated video. No GPU model inference is needed to render the recorded experiment.

```bash
python -m venv .voiceenv
# Activate the environment for your platform.
pip install edge-tts imageio-ffmpeg
python build_video.py
npx hyperframes@0.8.140 check
npx hyperframes@0.8.140 preview --background
npx hyperframes@0.8.140 render --fps 30 --quality delivery -o ../deliverables/document-verification-lab-en.mp4
```

`make_voice.py` regenerates one continuous English voice file via Edge TTS; this needs internet access. Changing the narration requires regenerating both voice and the film. To preserve this release, use the included voice and timing files.

The released film also contains licensed Pixabay music. The standalone track is not redistributed. Obtain it under its current license from the source in `../NOTICE.md` and place it at `assets/audio/ambient-piano.mp3` to reproduce the music bed. Without that optional file, the builder uses voice and the synthesized taps only.

`SPEC.md` records design choices; `REVIEW.md` records actual checks. `build_video.py` reads the displayed model scores from the experiment evidence. The numerical story and narration describe this frozen release; an assertion guards the main result counts. New experiments require updating the narration and story before rendering. Review thresholds and measured counts remain in the repository's results.
