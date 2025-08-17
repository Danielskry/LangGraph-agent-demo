# LangGraph Agent Demo 2024

A simplified web search agent using LangGraph, Pydantic, Tavily and Anthropic's Claude.

The app has a Django frontend and simple LangGraph app in `main.py`. The LangGraph app uses Pydantic models (classification) to decide when web search is needed.

<img width="1015" height="760" alt="langgraph_agent_demo" src="https://github.com/user-attachments/assets/8343833d-0dbf-4bc5-a9f3-b2c417eac2a0" />


## Getting Started

### Prerequisites

* Python 3.10 or higher
* Anthropic API key (for Claude)
* Tavily API key (for web search)
* Poetry (for dependency management)

### Setup

#### Configure Environment Variables

1. Create a `.env` file in the root directory
2. Add your API keys:
   ```
   ANTHROPIC_API_KEY=<your-api-key-here>
   TAVILY_API_KEY=<your-api-key-here>
   ```

#### Install Dependencies

For the backend:
```bash
poetry install
```

#### Run the Application

Start the application with:
```bash
python manage.py runserver
```

#### Access the Interface

Once running, access the chat interface at http://localhost:8000 and try:

- "What is the weather in Oslo?" ← Searches web
- "Explain machine learning" ← Uses knowledge
