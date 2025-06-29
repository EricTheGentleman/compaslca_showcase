from methods.prompt_builder_category import build_category_prompt
from methods.prompt_builder_material import build_material_prompt
from openai import OpenAI
import google.generativeai as genai
import anthropic
import json
import re

# === Token Usage Wrapper ===
class TokenUsageWrapper:
    def __init__(self, prompt_tokens, completion_tokens):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def to_dict(self):
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens
        }

# === Generic LLM Handler ===
def generic_llm_call(prompt, model_config):
    company = model_config.get("company", "OpenAI").lower()
    model_choice = model_config.get("model")
    key = model_config.get("api_key") or model_config.get("key")

    # === OpenAI ===
    if company == "openai":
        client = OpenAI(api_key=key)

        if model_choice.startswith("o3"):
            response = client.responses.create(
                model=model_choice,
                input=[{"role": "user", "content": prompt}],
                reasoning={"effort": "medium"}
            )
            response_text = response.output_text
            usage = response.usage
            token_usage = TokenUsageWrapper(
                prompt_tokens=usage.input_tokens,
                completion_tokens=usage.output_tokens
            )

        else:
            response = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "user", "content": prompt}],
                temperature=model_config.get("temperature"),
                max_tokens=model_config.get("max_tokens")
            )
            response_text = response.choices[0].message.content
            usage = response.usage
            token_usage = TokenUsageWrapper(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens
            )

    # === Anthropic (Claude) ===
    elif company == "anthropic":
        client = anthropic.Anthropic(api_key=key)

        response = client.messages.create(
            model=model_choice,
            max_tokens=model_config.get("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.content[0].text
        usage = response.usage
        token_usage = TokenUsageWrapper(
            prompt_tokens=usage.input_tokens,
            completion_tokens=usage.output_tokens
        )

    # === Gemini ===
    elif company == "gemini":
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_choice)
        response = model.generate_content(prompt)
        response_text = response.text
        usage = response.usage_metadata
        token_usage = TokenUsageWrapper(
            prompt_tokens=getattr(usage, "prompt_token_count", 0),
            completion_tokens=getattr(usage, "candidates_token_count", 0)
        )

    else:
        raise ValueError(f"Unsupported company: {company}")

    # === Parse and Return JSON ===
    try:
        cleaned = re.sub(r"```json|```", "", response_text).strip()
        parsed = json.loads(cleaned)
        return parsed, token_usage
    except Exception as e:
        raise ValueError(f"{company.capitalize()} returned invalid JSON:\n{response_text}") from e

# === Category Inference ===
def category_inference(bim_element, category_data, mode, config):
    prompt = build_category_prompt(bim_element, category_data, mode, config)
    model_config = config.get("category_inference_config", {})
    return generic_llm_call(prompt, model_config)

# === Material Inference ===
def material_inference(bim_element, material_data, mode, config, category=None):
    prompt = build_material_prompt(bim_element, material_data, mode, category, config)
    model_config = config.get("material_inference_config", {})
    return generic_llm_call(prompt, model_config)
