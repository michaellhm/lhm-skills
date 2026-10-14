# Local production recipes

## Proven stack and scope

- Video: https://github.com/remotion-dev/remotion
- Speech model: https://github.com/QwenLM/Qwen3-TTS
- Apple Silicon runtime: https://github.com/Blaizzy/mlx-audio

The pilot used Remotion 4.0.535, MLX Audio 0.5.9, Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit to audition a voice, then Qwen3-TTS-12Hz-1.7B-Base-4bit with the approved synthetic reference for subsequent speech. Verify package APIs, model licences and Remotion company licensing before a fresh setup. MLX is an Apple Silicon choice, not a portable requirement. On other hosts use a supported Qwen runtime or another agreed engine; do not silently substitute a different accent.

Keep dependencies in a project-local environment and model weights in a Git-ignored cache. Do not commit recordings, screenshots, model weights, secrets or generated client media into plugin source. The actual model assets remain in the verified project and should be named by digest in delivery records.

## Stable voice and cache

Use `load_model(...)` from `mlx_audio.tts.utils`. VoiceDesign supports `generate_voice_design(text, language, instruct)` for an audition. Base supports `generate(text, language, ref_audio, ref_text, ...)` for a common speaker reference. A fixed random seed with independent VoiceDesign calls did not lock the speaker in the pilot. One reusable reference did much better.

`ref_text` is the transcript of `ref_audio`, never the first sentence of the current revised script. The reference must remain accurate after hook revisions. Reuse approved narration where its content and voice settings have not changed.

Cache keys must include target text, model/version, voice/reference digest, reference transcript, seed and generation settings. Text-only keys can reuse stale audio after a voice change. Write the new audio manifest atomically after all sections are generated and verified. Keep the previous working manifest during generation. Strip neither the end of a spoken sentence nor meaningful pauses. Check actual generated content and duration.

## Review binding

The gate helper reads package-local `script.json`, `voice.json` and `audio-manifest.json`, hashes their bytes and the audio/reference files, and writes `approval.json` after explicit user approval. In `voice.json`, use `references` for the local audio paths that define speaker identity, for example:

```json
{"engine":"qwen3-tts-mlx","model":"verified model ID","reference_transcript":"Original reference speech","references":["voice/reference.wav"],"seed":42,"playback_rate":1.5}
```

Copy authorised external reference audio into this private package if necessary; do not commit it to the skill source. Visual-only changes are deliberately outside the script/audio approval digest. Publication is never implied by a passing check.

## Timeline and speed

Measure WAV durations from frames/sample rate, round scene lengths to whole frames and add a short pause. In Remotion, use one `Sequence` per scene with its narration. Keep cumulative start frames consistent with the same source fps.

For a 1.5x preview of a 30 fps timeline, the composition can play the unchanged frame count at 45 fps with narration and music `playbackRate={1.5}`. For 1.2x use 36 fps and 1.2 audio playback. Keep the source master unchanged; avoid changing durations, fps and playback rates in ways that apply the acceleration twice.

For a source MP4, FFmpeg can uniformly scale video timestamps and preserve voice pitch with `atempo`. With a full FFmpeg build use `setpts=PTS/rate` and `atempo=rate`. The pilot's bundled Remotion FFmpeg omitted `setpts`, so this worked:

```text
ffmpeg -itsscale 0.666666666667 -i source-master.mp4 -map 0:v:0 -map 0:a:0 -c:v copy -af atempo=1.5 -c:a aac -b:a 192k -movflags +faststart final-1.5x.mp4
```

On macOS the Remotion compositor binary may need `DYLD_LIBRARY_PATH` set to its own directory for bundled dylibs. Locate the package for the actual architecture. Verify output video/audio duration agreement with ffprobe; do not assume an exit code alone proves sync. Source master / 1.5 should match the intended final duration.

## Screenshots, music and export

Redact identifiers from the complete asset, not just the current crop, so later zooms cannot reveal them. Inspect edited pixels and render a frame from the moving crop. Use a screenshot to demonstrate an interface, not to imply the pictured clinic achieved example results or has a verified problem.

Original synthesized music is one subscription-free option. Licensed music can also work, but retain the licence/source and required attribution. Generate or trim the bed to the current source duration, then apply final speed consistently with the video/narration. Keep it below speech and listen at ordinary phone volume.

Pin a working Remotion dependency set. Render to versioned MP4 filenames, keep the original and comparison variants, check the opening/longest copy/CTA, then return the actual file and preview. The pilot's 1.5x export was about 56 seconds; that is evidence from one reel, not a universal length requirement.
