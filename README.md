# YVES: Virtual Engineering System (Core Engine)

YVES is a local, dual-LLM system built to act as a coding partner for software and computer engineering work. Instead of being another basic wrapper over a chat API, 
YVES routes queries through a custom matrix. This design splits technical coding logic from conversational personality elements.

The setup runs entirely on your local machine using Ollama. It relies on two models: Qwen2.5-Coder handles code analysis, while Llama3.2 manages natural conversation.

# System Architecture and Mechanics

YVES uses object-oriented patterns and dependency injection to keep things modular. The pipeline follows a specific flow:

```
       [User Input]
            │
            ▼
┌───────────────────────────┐
│ MemoryVault (ChromaDB)    │ ──► Vector-space semantic proximity calculation
└───────────────────────────┐
            │
            ▼
┌───────────────────────────┐
│     Intent Classifier     │
└───────────────────────────┘
            │
      ┌─────┴───────────────┐
      │ [Technical]         │ [Casual]
      ▼                     ▼
┌───────────────────┐ ┌───────────────────┐
│ Coder Component   │ │ Identity Layer    │ ──► Low-latency dialogue 
│ (Qwen2.5-Coder)   │ │ (Llama3.2 Persona)│     with environmental metadata
└───────────────────┘ └───────────────────┘
      │                     │
      ▼                     │
┌───────────────────┐       │
│ Identity Layer    │ ◄─────┘
│ (Context Fusion)  │
└───────────────────┘
            │
            ▼
   [Refined UI Output]
````

# The Codebase

The logic is split across several Python scripts:

*   **YvesEngine (engine_5.py):** The main controller. It intercepts user inputs, co-ordinates the routing, and tracks the state of the session.
*   **MemoryVault (retriever_5.py):** A local vector store built on ChromaDB. It indexes your source code files and uses a cosine-similarity table to figure out what you are trying to do when you ask a question.
*   **Coder (coder_5.py):** The technical runner. It runs Qwen2.5-Coder to analyse files or write code without any conversational overhead.
*   **YvesIdentity (identity_5.py):** The conversational layer. It formats the persona, pulls in local environment details like the current time, day, and operating system info, and formats everything using British English rules.
*   **HistoryManager (history_manager_5.py):** A thread-safe queue. It keeps a rolling buffer of the chat history to prevent the prompt context from filling up.
*   **Terminal (terminal_5.py):** A direct shell execution interface that lets the system run commands on your machine within set boundaries.

# Why I Built This

I built YVES because standard developer assistants did not fit my workflow as a computer engineering student. I wanted to solve a few specific problems:

*   **Custom Persona:** I wanted to build my own AI and customise its personality myself, rather than dealing with a generic, robotic chat assistant. I wanted a partner that works and talks the way I prefer.
*   **Better Context and Debugging:** I needed an assistant that can read my local files to understand the actual context of my projects. This makes it far more useful when I need help with complex debugging or working through system architecture.
*   **Absolute Privacy:** I wanted to keep my code and data private. Because YVES runs entirely on my own machine, everything stays local. My files are never sent over the internet or used to train other AI models.

# What YVES Does Now

*   **Intelligent Routing:** Instead of wasting tokens on a single massive model, YVES uses quick vector matching to classify your intent first. It only sends technical tasks to the heavy coding model.
*   **Automatic Code Indexing:** The system scans your active workspace, splits your code into logical blocks, and updates the local ChromaDB database.
*   **Local Awareness:** It checks your system clock, day, and operating system type to understand your current context.
*   **Unified Output:** It combines the raw output of the coding model with the conversational layer to produce a single markdown response.

# Planned Features

*   **Asynchronous Operations:** Transition the blocking pipeline to a non-blocking asyncio event loop to speed up execution.
*   **Background Tasks:** Set up background processes so the assistant can check files or complete tasks without direct user input.
*   **Voice and Audio:** Integrate voice input and local text-to-speech to allow spoken commands and real-time audio responses.

# Current Status & Development Notes

> **Developer Note:** This framework is an active, independent project I am using to experiment with local LLM co-ordination and vector database routing. Because this is a development workspace, some experimental pieces are still being ironed out.

## What is Working

*   **Intent Routing:** The MemoryVault initializes and updates the router collection in ChromaDB without issue, successfully sorting user prompts using vector similarity.
*   **Model Separation:** YvesEngine successfully isolates the conversational output (Llama 3.2) from the raw code analysis (Qwen 2.5-Coder).
*   **Context Retention:** The thread-safe history queue manages short-term memory reliably within set token limits.
*   **Workspace Scanning:** The system automatically and recursively indexes supported file types (.py, .js, etc.) into local embeddings.

## What I am Working on Next

*   **Terminal Integration:** The Terminal component exists as an independent class, but I have temporarily disconnected it from the main engine loop while I refine and secure the function-calling logic.
*   **Synchronous Bottleneck:** The pipeline currently runs synchronously. Heavy processing steps can cause noticeable pauses, which is why transitioning to an asynchronous setup is my main priority.
