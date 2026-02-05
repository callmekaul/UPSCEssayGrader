from langchain_openai import ChatOpenAI
from schemas import EvaluationSchema, OverallEvaluationSchema

model = ChatOpenAI(model="gpt-4o-mini")

structured_model = model.with_structured_output(EvaluationSchema)
overall_model = model.with_structured_output(OverallEvaluationSchema)