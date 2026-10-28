# Review record

The film follows one generated invoice through an internally consistent amount substitution, visual scoring, the actual held-out results, and a supplier-invoice workflow. A single continuous English narration is used. Runtime: 90.16 seconds including the ending hold. The model's score is explained when first introduced.

Inspected seven rendered frames at 7, 20, 36, 54, 67, 83 and 87.456 seconds. Corrected a caption-composition background that initially covered the scenes; the final contact sheet shows the actual source region and candidate. Restored punctuation from the narration script in the subtitle groups. Review bars use the same 80-region scale (3.75% and20%).

Final automated check: no lint errors or warnings, no runtime or layout errors, 72/72 contrast checks passed. Model values are taken from the experiment evidence; source image hashes and routing counts pass scripts/validate_evidence.py. The 24 injected errors remain separate from natural OCR results throughout.

Audio is one Edge TTS Andrew synthesis request, with phrase captions aligned to its returned word timings. Background music is mixed quietly with fades; synthesized taps mark scene boundaries. Levels and duration were measured; subjective pronunciation has not been independently listened to by a human reviewer. No claim of human listening QA is made.

Weakest shot: the three verifier inputs are smaller than the source-versus-candidate comparison. They establish the input structure; the preceding scene supplies the readable detail. This version favors an evidence walkthrough over stock footage or visual decoration.

The installed CLI supports timestamp snapshots rather than --review; the same scene midpoints were inspected with --at. The optional general-video skill updater was unavailable in that CLI; the installed core composition and validation contract was followed. CLI pinned to 0.8.140.

No video warnings retained. Public methodology contains licensing and limitations; the end frame contains the lab link and author.

Delivery verification: final MP4 inspected at 36s and83s after extraction from the encoded file. H.264, 1920×1080,30fps; AAC stereo48kHz;90.17s. Mix mean -20.0dBFS, peak -3.9dBFS. Render used hardware-GPU drawElement capture and completed in56.4s. Published video is embedded in the HF Space.
