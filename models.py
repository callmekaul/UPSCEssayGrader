from langchain_openai import ChatOpenAI
from schemas import CalibrationResult, EvaluationSchema

model = ChatOpenAI(model="gpt-4o-mini")

structured_model = model.with_structured_output(EvaluationSchema)
calibration_model = model.with_structured_output(CalibrationResult)