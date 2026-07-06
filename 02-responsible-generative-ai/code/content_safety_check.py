# pip install azure-ai-contentsafety --break-system-packages
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential
import os

client = ContentSafetyClient(
    endpoint=os.environ["CONTENT_SAFETY_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["CONTENT_SAFETY_KEY"]),
)

def is_safe(text: str, threshold: int = 2) -> bool:
    result = client.analyze_text(AnalyzeTextOptions(text=text))
    categories = [result.hate_result, result.self_harm_result,
                  result.sexual_result, result.violence_result]
    return all(c is None or c.severity <= threshold for c in categories)

def guarded_generate(prompt: str, model_call) -> str:
    if not is_safe(prompt):
        return "This request can't be processed. Please rephrase your question."
    output = model_call(prompt)
    if not is_safe(output):
        return "The generated response was withheld by our safety system."
    return output
