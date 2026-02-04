from langchain_openai import ChatOpenAI
from schemas import EvaluationSchema, GrammarEvaluation, OverallEvaluationSchema

model = ChatOpenAI(model="gpt-4o-mini")

structured_model = model.with_structured_output(EvaluationSchema)
grammar_model = model.with_structured_output(GrammarEvaluation)
overall_model = model.with_structured_output(OverallEvaluationSchema)