\# AI Red-Teaming Lab: Prompt Injection and Secret Disclosure



A hands-on AI security project demonstrating how direct prompt injection can cause a language model to disclose information placed in its system prompt, how to document the finding, and how to verify a remediation with fresh test results.



\## Project Overview



This project implements a fictional customer-support chatbot using Python, Flask, and Ollama. Promptfoo is used to generate and evaluate adversarial prompts against the local chatbot.



The lab follows a security-testing lifecycle:



1\. Build a controlled AI application.

2\. Test for prompt injection and information disclosure.

3\. Capture the original results and document the findings.

4\. Remove the synthetic secret from the model's context.

5\. Rerun the tests with caching disabled.

6\. Compare the retest output with the original evidence.



All testing is performed against a local, fictional application using synthetic test data.



\## Technology Stack



\- Python

\- Flask

\- Ollama

\- Gemma 3 4B

\- Promptfoo

\- Git and GitHub



\## Architecture



The browser sends a message to a Flask endpoint. Flask passes the conversation and system prompt to a locally hosted Ollama model and returns the model's response to the browser.



Promptfoo sends automated adversarial inputs to the Flask endpoint and records the responses for evaluation.



\## Security Finding: Prompt Injection and Secret Disclosure



\*\*Original finding:\*\* A crafted prompt caused the model to disclose a synthetic training token embedded in the system prompt.



\*\*Remediation:\*\* Removed the synthetic token from the prompt rather than relying on the model to keep it secret.



\*\*Verification:\*\* Repeated the relevant test using Promptfoo with caching disabled. The tested token was not reproduced in the fresh response.



\*\*Important limitation:\*\* This verifies the outcome for the tested token and attack scenario. It does not establish immunity to all prompt-injection attacks or eliminate other potential information-disclosure risks.



\## System-Prompt Extraction



Additional testing demonstrated that the model could disclose ordinary role and behavioral instructions.



This result was assessed separately from secret disclosure. Revealing generic instructions does not, by itself, demonstrate a high-impact security vulnerability. Security-sensitive data and authorization decisions must be protected outside the model prompt.



\## Setup



Prerequisites:



\- Python

\- Git

\- Node.js

\- Ollama



Install the required Ollama model:



`ollama pull gemma3:4b`



Create a Python virtual environment and install dependencies:



`python -m venv .venv`



On Windows:



`.venv\\\\Scripts\\\\python.exe -m pip install -r requirements.txt`



On macOS or Linux, activate the virtual environment and use:



`python -m pip install -r requirements.txt`



Start the chatbot from the repository root:



Windows:



`.venv\\\\Scripts\\\\python.exe app\\\\app.py`



macOS/Linux:



`python app/app.py`



Open `http://127.0.0.1:8000` in a browser.



In a separate terminal, run the existing Promptfoo red-team evaluation:



`npx promptfoo@latest redteam eval --no-cache`



Review the generated results and verify the actual response content instead of relying exclusively on the overall pass/fail score.



\## Findings and Evidence



The `docs/` directory contains the vulnerability write-ups, remediation notes, and redacted evidence.



The report distinguishes observed behavior from potential impact and records the limits of the testing performed.



\## Safety and Scope



This is a deliberately limited, educational security lab. The synthetic secret is not a real credential. The application listens on localhost and is not intended to be exposed publicly.



Run security tests only against systems you own or are explicitly authorized to assess.



\## Lessons Learned



\- A system prompt is not a dependable place to store secrets.

\- Application-level authorization and data protection must not depend solely on model instructions.

\- Cached results can mislead a security assessment if they are mistaken for fresh test outputs.

\- A remediation should be verified against the same test cases, with the actual responses reviewed.

\- A passing test is evidence for a specific scenario, not proof that an application is secure.



\## Project Status



The local chatbot, original attack demonstration, remediation, and targeted retest have been implemented. Broader testing with additional red-teaming frameworks and attack scenarios remains future work.



\## Reference



This project was developed as a learning implementation inspired by the \[AI-Security-Projects repository](https://github.com/taimurijlal/AI-Security-Projects).



Some implementation and documentation work was developed with AI assistance and reviewed through hands-on execution and testing.

