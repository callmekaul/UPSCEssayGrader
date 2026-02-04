from langchain_openai import ChatOpenAI
from schemas import EvaluationSchema

model = ChatOpenAI(model="gpt-4o-mini")

structured_model = model.with_structured_output(EvaluationSchema)