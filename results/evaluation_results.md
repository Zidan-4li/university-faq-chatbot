# Evaluation Results

27 test questions were run against the University FAQ Chatbot, covering
direct questions matching document wording, reworded/casual phrasing,
and out-of-scope questions the chatbot should refuse to answer.

## Results Table

| # | Question | Status |
|---|----------|--------|
| 1 | What are the admission requirements for undergraduate programs? | Correct |
| 2 | When is the application deadline? | Correct |
| 3 | What documents are required for application? | Correct |
| 4 | What is the tuition fee for the BIT program? | Correct |
| 5 | Are scholarships available? | Correct |
| 6 | What courses are offered in the BIT program? | Correct |
| 7 | Is there a final year project? | Correct |
| 8 | Are internships part of the curriculum? | Correct |
| 9 | Can students switch programs after enrollment? | Correct |
| 10 | How many credit hours are required to graduate? | Correct |
| 11 | What is the minimum CGPA required to remain in good standing? | Correct |
| 12 | Can students defer a semester? | Correct |
| 13 | What is the policy on late assignment submissions? | Correct |
| 14 | What is the policy on academic dishonesty? | Correct |
| 15 | What are the library operating hours? | Correct |
| 16 | Is on-campus accommodation available? | Correct |
| 17 | Where can students seek counseling support? | Correct |
| 18 | What sports facilities are there? | Correct |
| 19 | How can students contact the Academic Office? | Correct |
| 20 | Who do students contact for IT support? | Correct |
| 21 | Who should students contact regarding internship placements? | Correct |
| 22 | Can I get a scholarship? | Correct |
| 23 | What happens if I submit my assignment late? | Correct |
| 24 | Is there mental health support on campus? | Correct |
| 25 | What's the weather like today? | Correct (refused appropriately) |
| 26 | What is the tuition fee for the Medicine program? | Correct (refused appropriately) |
| 27 | Who is the Prime Minister of Malaysia? | Correct (refused appropriately) |

## Summary Statistics

- **Total questions tested:** 27
- **Direct questions (Category A):** 21/21 correct (100%)
- **Reworded/casual phrasing (Category B):** 3/3 correct (100%)
- **Out-of-scope refusals (Category C):** 3/3 correctly refused (100%)
- **Overall accuracy:** 27/27 (100%)

## Observations

- The chatbot correctly answered all direct questions matching the source
  document's structure and content.
- Reworded/casual phrasing (e.g. "Can I get a scholarship?" instead of
  "Are scholarships available?") was handled correctly, demonstrating
  that semantic retrieval (via embeddings) works beyond exact keyword
  matching.
- Out-of-scope questions were consistently refused rather than answered
  with fabricated information, confirming the grounding/prompt engineering
  approach is effective at reducing hallucination.
- During earlier, less formal testing (outside this evaluation set), some
  vague or under-specified questions (e.g. "What is the tuition fees"
  without naming a program) did not retrieve a correct answer. This
  highlights a limitation: retrieval accuracy can depend on how
  specifically a question is phrased, discussed further in Chapter 6.3.
