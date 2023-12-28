import os
from fastapi import FastAPI, HTTPException
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from uvicorn import run
from pydantic import BaseModel, Field
import torch
from config import Settings

SETTINGS = Settings()

print(f'model_path: {SETTINGS.model_path}')

# 判断是否已经设置了DEVICE，且不为空字符串或None
DEVICE = getattr(SETTINGS, 'device', 'cuda' if torch.cuda.is_available() else 'cpu')
print(f'DEVICE: {DEVICE}')

model = MBartForConditionalGeneration.from_pretrained(SETTINGS.model_path).to(SETTINGS.device)
tokenizer = MBart50TokenizerFast.from_pretrained(SETTINGS.model_path)

class TranslationRequest(BaseModel):
    source_lang: str = Field('zh', description="原始文本语言类型")
    target_lang: str = Field('en', description="目标文本语言类型")
    text: str = Field(None, description="需要翻译的文本内容")

class LanguageInfo:
    def __init__(self, full_code_with_suffix: str, full_name: str):
        self.full_code_with_suffix = full_code_with_suffix
        self.full_name = full_name
        
# Mapping of language prefixes to LanguageInfo objects
lang_suffix_map = {
    "ar": LanguageInfo("ar_AR", "Arabic"),
    "cs": LanguageInfo("cs_CZ", "Czech"),
    "de": LanguageInfo("de_DE", "German"),
    "en": LanguageInfo("en_XX", "English"),
    "es": LanguageInfo("es_XX", "Spanish"),
    "et": LanguageInfo("et_EE", "Estonian"),
    "fi": LanguageInfo("fi_FI", "Finnish"),
    "fr": LanguageInfo("fr_XX", "French"),
    "gu": LanguageInfo("gu_IN", "Gujarati"),
    "hi": LanguageInfo("hi_IN", "Hindi"),
    "it": LanguageInfo("it_IT", "Italian"),
    "ja": LanguageInfo("ja_XX", "Japanese"),
    "kk": LanguageInfo("kk_KZ", "Kazakh"),
    "ko": LanguageInfo("ko_KR", "Korean"),
    "lt": LanguageInfo("lt_LT", "Lithuanian"),
    "lv": LanguageInfo("lv_LV", "Latvian"),
    "my": LanguageInfo("my_MM", "Burmese"),
    "ne": LanguageInfo("ne_NP", "Nepali"),
    "nl": LanguageInfo("nl_XX", "Dutch"),
    "ro": LanguageInfo("ro_RO", "Romanian"),
    "ru": LanguageInfo("ru_RU", "Russian"),
    "si": LanguageInfo("si_LK", "Sinhala"),
    "tr": LanguageInfo("tr_TR", "Turkish"),
    "vi": LanguageInfo("vi_VN", "Vietnamese"),
    "zh": LanguageInfo("zh_CN", "Chinese"),
    "af": LanguageInfo("af_ZA", "Afrikaans"),
    "az": LanguageInfo("az_AZ", "Azerbaijani"),
    "bn": LanguageInfo("bn_IN", "Bengali"),
    "fa": LanguageInfo("fa_IR", "Persian"),
    "he": LanguageInfo("he_IL", "Hebrew"),
    "hr": LanguageInfo("hr_HR", "Croatian"),
    "id": LanguageInfo("id_ID", "Indonesian"),
    "ka": LanguageInfo("ka_GE", "Georgian"),
    "km": LanguageInfo("km_KH", "Khmer"),
    "mk": LanguageInfo("mk_MK", "Macedonian"),
    "ml": LanguageInfo("ml_IN", "Malayalam"),
    "mn": LanguageInfo("mn_MN", "Mongolian"),
    "mr": LanguageInfo("mr_IN", "Marathi"),
    "pl": LanguageInfo("pl_PL", "Polish"),
    "ps": LanguageInfo("ps_AF", "Pashto"),
    "pt": LanguageInfo("pt_XX", "Portuguese"),
    "sv": LanguageInfo("sv_SE", "Swedish"),
    "sw": LanguageInfo("sw_KE", "Swahili"),
    "ta": LanguageInfo("ta_IN", "Tamil"),
    "te": LanguageInfo("te_IN", "Telugu"),
    "th": LanguageInfo("th_TH", "Thai"),
    "tl": LanguageInfo("tl_XX", "Tagalog"),
    "uk": LanguageInfo("uk_UA", "Ukrainian"),
    "ur": LanguageInfo("ur_PK", "Urdu"),
    "xh": LanguageInfo("xh_ZA", "Xhosa"),
    "gl": LanguageInfo("gl_ES", "Galician"),
    "sl": LanguageInfo("sl_SI", "Slovene"),
}

def get_lang_info(language_code: str):
    lang_info = lang_suffix_map.get(language_code)
    if lang_info is None:
        raise HTTPException(status_code=404, detail=f"Language code {language_code} not found")
    return lang_info


app = FastAPI(title='API-翻译服务')

@app.get("/v1/lang/support", summary='获取支持的语种')
async def get_languages(lang_code: str = None):
    if lang_code is None:
        # Return information about all languages as an array
        languages_info = [
            {"code": code, "full_code": info.full_code_with_suffix, "name": info.full_name}
            for code, info in lang_suffix_map.items()
        ]
        return languages_info
    else:
       # Return information about a specific language
        lang_info = get_lang_info(lang_code)
        if lang_info is None:
            raise HTTPException(status_code=404, detail=f"Language code {lang_code} not found")
        return {
            "code": lang_code,
            "full_code": lang_info.full_code_with_suffix,
            "name": lang_info.full_name,
        }
 
@app.post("/v1/lang/translate", summary='文本翻译')
async def translate_text(request: TranslationRequest):
    source_lang = request.source_lang
    target_lang = request.target_lang
    
   # Get the LanguageInfo object based on the language prefix
    source_lang_info = get_lang_info(request.source_lang)
    target_lang_info = get_lang_info(request.target_lang)

    # Access the properties of the LanguageInfo object
    full_source_lang = source_lang_info.full_code_with_suffix
    full_target_lang = target_lang_info.full_code_with_suffix

    text = request.text
    
    tokenizer.src_lang = full_source_lang
    encoded_text = tokenizer(text, return_tensors="pt")
    forced_bos_token_id = tokenizer.lang_code_to_id.get(full_target_lang)
    if forced_bos_token_id is None:
        raise HTTPException(status_code=400, detail=f"Invalid target language code: {target_lang}")
    
    # Generate translation
    if DEVICE == 'cuda':
        # If using CUDA, move tensors to the GPU
        encoded_text = {key: value.to('cuda') for key, value in encoded_text.items()}

    generated_tokens = model.generate(**encoded_text, forced_bos_token_id=forced_bos_token_id)
    
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    return {"source_lang": source_lang, "target_lang": target_lang, "text": text, "translated_text": translated_text}

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=23129)
