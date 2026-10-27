"""
ThreatLens AI - RAG Security Assistant Engine
Grounds security questions and anomaly alerts in retrieved MITRE ATT&CK,
NIST SP 800-61, and CIC-IDS2017 technical documentation with strict citations.
Supports external LLM APIs (Groq, OpenAI, Gemini) and local extractive synthesis.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.retriever import ThreatLensRetriever

load_dotenv()

class ThreatLensSecurityAssistant:
    """RAG-powered cybersecurity incident response and guidance assistant."""
    
    def __init__(self, retriever: Optional[ThreatLensRetriever] = None):
        self.retriever = retriever or ThreatLensRetriever()
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()

    def generate_response(self, query: str, top_k: int = 4, score_threshold: float = 0.25) -> Dict[str, Any]:
        """
        Retrieves relevant passages and generates a grounded response with citations.
        """
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k, score_threshold=score_threshold)
        
        # Guardrail: Insufficient evidence check
        if not retrieved_chunks:
            return {
                "query": query,
                "answer": (
                    "**Insufficient Evidence in Knowledge Base:**\n\n"
                    "The indexed cybersecurity documents (MITRE ATT&CK, NIST SP 800-61, and CIC-IDS2017 guide) "
                    "do not contain sufficient verified evidence to reliably answer this query. "
                    "Please verify your query terminology or consult enterprise-specific threat intelligence."
                ),
                "citations": [],
                "source_used": "None",
                "retrieved_count": 0
            }
            
        # Format context and citations
        citations = []
        context_blocks = []
        for i, c in enumerate(retrieved_chunks, 1):
            citations.append({
                "citation_id": f"[{i}]",
                "title": c["title"],
                "section": c["section"],
                "source": c["source"],
                "page": c.get("page", 1),
                "score": c["score"],
                "excerpt": c["text"][:280] + ("..." if len(c["text"]) > 280 else "")
            })
            context_blocks.append(f"Source [{i}] ({c['title']} - {c['section']}):\n{c['text']}")
            
        context_str = "\n\n".join(context_blocks)
        
        # Try external LLM API if available
        llm_answer = self._try_llm_generation(query, context_str)
        if llm_answer:
            return {
                "query": query,
                "answer": llm_answer,
                "citations": citations,
                "source_used": "LLM Grounded Synthesis",
                "retrieved_count": len(retrieved_chunks)
            }
            
        # Local Grounded Synthesis Engine (Zero-cost, offline-ready fallback)
        local_answer = self._synthesize_local_response(query, retrieved_chunks)
        return {
            "query": query,
            "answer": local_answer,
            "citations": citations,
            "source_used": "Local Grounded Engine",
            "retrieved_count": len(retrieved_chunks)
        }

    def _try_llm_generation(self, query: str, context: str) -> Optional[str]:
        """Attempts generation with available external LLM providers."""
        system_prompt = (
            "You are ThreatLens AI, a specialized cybersecurity operations assistant. "
            "Your role is to assist security analysts by synthesizing grounded incident response guidance "
            "strictly based on the provided technical sources.\n"
            "CRITICAL RULES:\n"
            "1. Ground all claims directly in the provided context. Cite sources using [1], [2], etc.\n"
            "2. If the context does not contain the answer, explicitly state that evidence is insufficient.\n"
            "3. DO NOT claim that a network flow anomaly score or high packet rate proves an actual security incident. "
            "A model score reflects statistical pattern deviation, not definitive proof of compromise.\n"
            "4. Maintain a professional, actionable SOC analyst tone with structured headings and bullet points."
        )
        user_prompt = f"Context Material:\n{context}\n\nAnalyst Question: {query}"
        
        # 1. Groq
        if self.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_api_key)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=650
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"Notice: Groq API call failed ({e}). Attempting next provider.")
                
        # 2. OpenAI
        if self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=650
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Notice: OpenAI API call failed ({e}).")
                
        return None

    def _synthesize_local_response(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        """
        Deterministic, offline synthesis engine that extracts actionable guidelines,
        indicators, and containment protocols directly from top matching chunks.
        """
        primary = chunks[0]
        secondary = chunks[1] if len(chunks) > 1 else None
        
        paragraphs = []
        paragraphs.append(
            f"Based on **{primary['title']}** (Section: *{primary['section']}*) [1], "
            f"here are the grounded security findings and incident-response recommendations:"
        )
        
        # Extract structured points from primary chunk
        raw_lines = primary["text"].split("\n")
        bullet_points = [line.strip() for line in raw_lines if line.strip().startswith(("-", "1.", "2.", "3.", "•", "*"))]
        
        if bullet_points:
            paragraphs.append("\n**Key Technical Indicators & Procedures:**")
            for bp in bullet_points[:4]:
                paragraphs.append(f"{bp} [1]")
        else:
            paragraphs.append(f"\n> \"{primary['text'][:250]}...\" [1]")
            
        if secondary:
            paragraphs.append(
                f"\n**Corroborating Guidance ({secondary['title']} - *{secondary['section']}* [2]):**"
            )
            sec_lines = [l.strip() for l in secondary["text"].split("\n") if l.strip().startswith(("-", "1.", "2.", "3."))]
            if sec_lines:
                for bp in sec_lines[:2]:
                    paragraphs.append(f"{bp} [2]")
            else:
                paragraphs.append(f"> \"{secondary['text'][:220]}...\" [2]")
                
        paragraphs.append(
            "\n*Analyst Note:* The observed traffic metrics represent statistical model scores. "
            "In accordance with NIST SP 800-61 triage principles, cross-reference these flow indicators "
            "with endpoint authentication logs and firewall rules before executing blocking actions."
        )
        
        return "\n".join(paragraphs)

    def explain_alert(self, port: int, anomaly_score: float, top_features: str, classification: str) -> Dict[str, Any]:
        """
        Convenience workflow bridging the Deep Learning Classifier alert with RAG guidance.
        """
        query = (
            f"The network intrusion model flagged a connection targeting destination port {port} "
            f"with anomaly score {anomaly_score:.2f} ({classification}). Top contributing features include: {top_features}. "
            f"What specific adversary techniques, triage checks, and containment procedures should be investigated?"
        )
        return self.generate_response(query, top_k=3)

if __name__ == "__main__":
    assistant = ThreatLensSecurityAssistant()
    sample_q = "What should I investigate when a network flow shows an unusual packet rate?"
    print(f"\nQuery: {sample_q}\n")
    res = assistant.generate_response(sample_q)
    print("--- ASSISTANT ANSWER ---")
    print(res["answer"])
    print("\n--- CITATIONS ---")
    for cit in res["citations"]:
        print(f"{cit['citation_id']} {cit['title']} | {cit['section']} (Relevance: {cit['score']})")
