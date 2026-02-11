import os
from langchain_openai import ChatOpenAI
from schemas import EvaluationSchema, OverallEvaluationSchema

# Set temperature=0 for consistent, deterministic outputs
model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY", ""))

structured_model = model.with_structured_output(EvaluationSchema)
overall_model = model.with_structured_output(OverallEvaluationSchema)