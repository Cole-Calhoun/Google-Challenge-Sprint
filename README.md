Challenge 1: Gemini Prompt Security - Defense-in-Depth Implementation
BLUFF: I engineered a secure, domain-restricted Generative AI agent designed to function strictly as an IT/Coding Assistant. By moving beyond simple prompt engineering and implementing a multi-layered "Defense-in-Depth" architecture, I successfully mitigated prompt injection risks, prevented domain drift, and eliminated hallucinations. The system utilizes Google Model Armor for network-level defense and a secondary "Auditor" model for semantic logic validation, ensuring code is only generated when security and context confidence scores exceed 70%.

Challenge Objective
The goal was to demonstrate how to program a secure Generative AI system. Rather than creating a standard open-ended chatbot, which is vulnerable to jailbreaks and "creative" hallucinations, I architected a system that validates user intent before processing requests.

Solution Architecture
I implemented a four-stage pipeline to enforce security and operational confinement:

Network Security (The Shield):

Integrated Google Model Armor (StarKiller_MA) using strict regional endpoints (us-central1).

Function: Automatically blocks prompt injection attacks (e.g., "Ignore previous instructions"), jailbreaks, and malicious URIs before they reach the LLM.

Semantic Domain Classification (The Gatekeeper):

Implemented a semantic analysis layer that evaluates the relevance of a topic rather than relying on brittle keyword lists.

Function: Dynamically categorizes inputs. Queries regarding "Network Address Translation" are accepted, while unrelated topics like "Cooking" or "Sports" are immediately rejected with a domain confinement message.

Contextual Integrity Audit (The Auditor):

Deployed a dedicated "Auditor" agent (Gemini 2.5 Pro) with strict system instructions to prevent "creative bridging."

Function: Compares the user's Topic against the provided Specifications. If a user provides a valid topic (e.g., "Cables") but nonsense details (e.g., "Star Wars movies"), the Auditor returns a low confidence score and blocks the request.

Secure Code Generation (The Expert):

Only upon passing all prior gates is the "Worker" model invoked.

Function: Generates production-grade code with enforced system constraints against PII, malware, and destructive commands.

Validation Methodology
The system was stress-tested against three specific vectors to prove robustness:

Safe Path: Verified valid IT requests generated accurate code.

Domain Drift: Verified that non-IT topics were semantically recognized and rejected without hallucination.

Logic Attacks: Verified that attempts to trick the model with conflicting contexts (valid topic/invalid details) were caught by the logic auditor.

Technical Implementation
Platform: Vertex AI Colab Enterprise

Model: gemini-2.5-pro (Latest Stable Release)

Security Library: google-cloud-modelarmor (v0.3.0)

Key Feature: Regional endpoint configuration to resolve IAM/routing conflicts and ensure compliance with localized security policies.
