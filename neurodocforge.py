from gradio_helper_genai import make_demo
import openvino_genai as ov_genai
import sys
from llm_config import get_llm_selection_widget
from llm_config import SUPPORTED_LLM_MODELS

device="CPU"
model_dir="Meta-Llama-3-8B-Instruct-ov"
model_configuration = ov_genai.GenerationConfig()
model_languages = "English"
model_configuration = SUPPORTED_LLM_MODELS["English"]["llama-3-8b-instruct"]
pipe = ov_genai.LLMPipeline(str(model_dir), device)

doc = make_demo(pipe,model_configuration, model_dir, "english", "CPU")

try:
    doc.launch(debug=True)
except Exception:
    doc.launch(debug=True, share=True)
