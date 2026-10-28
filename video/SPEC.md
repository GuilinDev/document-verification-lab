# Document Verification Lab — film specification

- Canvas 1920×1080, 30fps. Paper #f6f6ef, ink #163431, teal #096b5b, error #a52d24. No gradients, glowing dashboards, stock office montages, invented GPU hardware, or generic AI iconography.
- Safe area x192–1728, y108–972 for critical copy. Primary titles 64px, evidence 31–38px, subtitles 29px. Inter with local font assets. Content uses at least 40% of each frame for the invoice, model input images or numerical results.
- Continuous narration follows one example. Hard cuts at paragraph boundaries; 0.45s content entrances, small 18px vertical movement. Highlight values with a teal/rust rule; no arbitrary pulses.
- Scene 1: actual generated invoice 0040 left; source crop and total 6,416.03 right. Establish document automation question.
- Scene 2: source crop and controlled ×10 candidate, including all four amounts. Highlight internally consistent arithmetic. Explicit stress-test label.
- Scene 3: original image, candidate text and actual rendered candidate converge on binary consistency output. Correct and altered scores from evidence.json; show score meaning in plain words.
- Scene 4: 120 input pages, 40 calibration, 80 test. Proportional bars for 3 versus16 reviews, both catch3 errors; 13 added correct reviews.
- Scene 5: separate stress results: 24/24 routed, zero by rules. Keep injected label in title.
- Scene 6: supplier invoice → evidence/review → PO/receipt checks. End with author and HF lab URL; no end-card material credits.
- BGM -30dB beneath voice, 1s fade in/2s fade out. Generated soft tap at key state changes at -30dB; no transition whooshes. Mix peak below -1dBFS.
- Captions grouped by sentence/phrase, at most two lines inside y930–1010. One subtitle layer over all scenes; no text overlap with main content.
