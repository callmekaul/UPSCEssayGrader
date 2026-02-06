# 📝 UPSC Essay Evaluator

An AI-powered essay evaluation tool designed to analyze and provide detailed feedback on UPSC (Union Public Service Commission) essays. Built with Streamlit, LangChain, and LangGraph, this application uses advanced language models to evaluate essays against specific criteria and provide comprehensive examiner-style reports.

## Features

- **Automated Essay Analysis**: Leverages AI to evaluate essays against multiple evaluation criteria
- **Detailed Criterion-Based Feedback**: Each essay is evaluated across specific dimensions (e.g., introduction, conclusion, clarity, structure)
- **Annotated Feedback**: Identifies specific issues in the essay with suggestions for improvement
- **Overall Assessment**: Generates a comprehensive senior examiner report with strengths and weaknesses
- **Interactive Web Interface**: User-friendly Streamlit interface for easy essay submission and result viewing
- **Metadata Extraction**: Automatically calculates word count, paragraph count, and average paragraph length

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) - Interactive web interface
- **LLM Framework**: [LangChain](https://www.langchain.com/) - Language model integration
- **Orchestration**: [LangGraph](https://python.langchain.com/docs/langgraph/) - Agentic workflow management
- **Language Model**: OpenAI GPT (via LangChain-OpenAI)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/) - Type-safe data schemas
- **Environment Management**: Python-dotenv

## Architecture

The application uses a graph-based evaluation pipeline:

1. **Metadata Node**: Extracts essay statistics (word count, paragraphs, etc.)
2. **Intro/Conclusion Extractor**: Identifies and separates introduction and conclusion sections
3. **Evaluation Nodes**: Multiple criterion-based evaluators that assess specific aspects of the essay
4. **Overall Evaluation Node**: Synthesizes individual evaluations into a comprehensive report

## Installation

### Prerequisites
- Python 3.10 or higher
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd EssayGrader
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Run the Streamlit App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### Steps to Evaluate an Essay

1. Enter the **Essay Topic** in the text input field
2. Paste your **Essay** in the text area
3. Click the **"Evaluate Essay"** button
4. View the comprehensive evaluation report including:
   - Overall examiner report
   - Annotated essay with specific feedback
   - Criterion-wise evaluations
   - Strengths and weaknesses summary

### Run as a Script

For programmatic usage, use `main.py`:

```python
from build_graph import workflow
from schemas import EssayState

topic = "It's best to see Life as a journey, not a destination."
essay = "Your essay text here..."

initial_state: EssayState = {
    "topic": topic,
    "essay": essay
}

result = workflow.invoke(initial_state)
```

## Project Structure

- **`app.py`** - Streamlit web application interface
- **`main.py`** - Script for programmatic essay evaluation
- **`build_graph.py`** - Defines the LangGraph evaluation workflow
- **`nodes.py`** - Individual evaluation nodes for the graph
- **`schemas.py`** - Pydantic data models for type safety
- **`criteria_registry.py`** - Registry of evaluation criteria
- **`models.py`** - LLM model configurations
- **`utils.py`** - Utility functions for annotation rendering and formatting
- **`requirements.txt`** - Python package dependencies

## Evaluation Criteria

The evaluator assesses essays based on multiple criteria registered in the `criteria_registry.py` file. Each criterion provides:
- Specific rubric guidelines
- Severity levels for identified issues (error/warning)
- Detailed feedback structure

## Output Format

The evaluation includes:

1. **Overall Examiner Report**: A 120-180 word senior examiner assessment
2. **Essay-Level Strengths**: 3-5 major strengths identified
3. **Essay-Level Weaknesses**: 3-5 major weaknesses identified
4. **Criterion-Specific Feedback**: For each evaluation criterion:
   - Rating (Excellent, Good, Average, Poor)
   - 2-3 sentence examiner feedback
   - Annotated issues with suggestions

## Configuration

### Environment Variables

Required:
- `OPENAI_API_KEY` - Your OpenAI API key

## Requirements

See [requirements.txt](requirements.txt) for the complete list of dependencies. Key packages include:
- streamlit
- langchain & langchain-openai
- langgraph
- pydantic
- python-dotenv
- openai

## License

[Add your license information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions, please open an issue in the GitHub repository.

---

**Note**: This tool requires an OpenAI API key and will incur API usage costs proportional to the length and number of essays evaluated.
