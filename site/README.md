---
title: Document Verification Lab
emoji: 🔎
colorFrom: green
colorTo: gray
sdk: static
app_file: index.html
pinned: false
license: mit
short_description: Explore OCR evidence and visual verification tradeoffs
---

# Document Verification Lab

An interactive replay of real MiniCPM-OCR and OCR Jev inference on 120 generated invoice regions, with 48 separate stress candidates. By Guilin Zhang.

Explore source pixels, extracted text, rendered candidates and raw scores. Adjust the review threshold and compare with simple rules. GPU calls were recorded locally; this static Space does not run live inference.

[Watch the full USD workflow · 1:45](https://huggingface.co/spaces/guilindev/document-verification-lab/resolve/main/walkthrough.mp4): upload, OCR, visual comparison, classification head, score-based review, correction, and downstream invoice checks. The default case is DVL-0090, with a $4,271.98 source total and a deliberately altered $42,719.80 candidate.

[Code, methodology, source data and model revisions](https://github.com/GuilinDev/document-verification-lab)

Main result: on 80 held-out regions, rules caught all three natural errors. Adding the verifier increased review from 3 to 16 cases, including 13 correct items. On 24 separately injected, internally consistent currency/amount errors, the verifier caught all 24 that rules missed. No fine-tuning was performed.

Models: [MiniCPM-OCR 1.0](https://huggingface.co/openbmb/MiniCPM-OCR-1.0) and [MiniCPM-OCR Jev](https://huggingface.co/openbmb/MiniCPM-OCR-Jev), OpenBMB, Apache-2.0. Project code and generated data: MIT. Video music licensed for synchronized use; standalone track excluded.
