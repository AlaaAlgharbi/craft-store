from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
from django.conf import settings
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from transformers import AutoTokenizer, AutoModel

# MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# model_path = settings.MODEL_PATH
# tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
# model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)



model_id = "AlaaAlgharbi/craft-model"
hf_token = os.getenv("HF_TOKEN")  # تأكد أنك خزّنته في البيئة

tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_token)
model = AutoModel.from_pretrained(model_id, use_auth_token=hf_token)

def get_sentiment(comment):
    # تجهيز المدخلات (تقليم النص وتعبئته بأن تكون الطول ثابت)
    inputs = tokenizer(comment, return_tensors="pt", truncation=True, max_length=128, padding=True)
    # الحصول على النتائج (لوغيتس)
    # تحسين الأداء باستخدام no_grad
    with torch.no_grad():
        outputs = model(**inputs)
    scores = outputs.logits[0].detach().numpy()
    # تحويل الدرجات إلى احتمالات باستخدام softmax
    probs = softmax(scores)
    # تتراوح تقييمات النموذج عادةً من 1 إلى 5
    rating = probs.argmax() + 1   # نضيف 1 لأن الفهارس تبدأ من 0
    return rating



# 1: مشاعر سلبية جدًا.

# 2: مشاعر سلبية.

# 3: مشاعر محايدة.

# 4: مشاعر إيجابية.

# 5: مشاعر إيجابية جدًا.

# from transformers import AutoTokenizer, AutoModelForSequenceClassification

# MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"

# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# # حفظ النموذج والمحزز في مجلد "model"
# tokenizer.save_pretrained("./model")
# model.save_pretrained("./model")

# print("تم حفظ النموذج والمحزز في المجلد المحلي.")
