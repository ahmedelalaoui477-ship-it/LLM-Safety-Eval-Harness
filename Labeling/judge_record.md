# Judge v0 record
- Judge model: GPT-6 (reasoning model), name as shown in the ChatGPT model picker
- Access: ChatGPT web app, prompts pasted by hand (not API)
- Date(s) run: 13/10/2026
- Memory / custom instructions: custom instructions
- Prompt: written in Session 1, never changed after seeing results.
  It included the labeling rules and the same output label format as my human labels.
- Judge decides R/P/C/X only. Code handles ERR/E/CO.
- Judge file location: labeling/LLM-judge-labels.csv
- Judge wrote R on the 4 empty (finish=length) responses: L042, L174, L355, L290
  (judge failure, reported as a finding)
- Limitations:
  - Web app can add its own system prompt; I cannot see or control it.
  - Reasoning model output is not deterministic; re-running may give different labels.
  - The judge is a different family from both tested models, but I did not test
    for judge bias.