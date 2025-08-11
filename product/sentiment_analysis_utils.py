# من الأفضل استخدام نموذج التصنيف مباشرة بدل AutoModel لتبسيط الكود وتقليل التعقيد
# والحفاظ على نفس السلوك مع logits.
# MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# model_path = settings.MODEL_PATH
# tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
# model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)

from django.conf import settings
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # الإبقاء عليها كما وضعتها
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
# model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# model_path = settings.MODEL_PATH
# tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
# model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)

model_id = "AlaaAlgharbi/craft-model"
hf_token = os.getenv("HF_TOKEN")  # تأكد أنك خزّنته في البيئة

# تحميل الـ tokenizer والنموذج من هبنج فيس (أو من المسار المحلي كما في التعليقات أعلاه)
tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
model = AutoModelForSequenceClassification.from_pretrained(model_id, token=hf_token)
# تهيئة النموذج للوضع التنبؤي فقط
model.eval()

# اختيار الجهاز تلقائيًا (GPU إن وُجد)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


def get_sentiment(comment):
    # تجهيز المدخلات (تقليم النص وتعبئته بأن تكون الطول ثابت)
    inputs = tokenizer(
        comment,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        padding=True
    )
    # نقل التنسورات للجهاز المناسب
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # الحصول على النتائج (لوغيتس)
    # تحسين الأداء باستخدام no_grad / inference_mode
    with torch.inference_mode():
        outputs = model(**inputs)

    # تحويل الدرجات إلى احتمالات باستخدام softmax (من PyTorch لتقليل الاعتمادات)
    logits = outputs.logits  # شكلها [batch_size, num_labels]
    probs = torch.softmax(logits, dim=-1)[0]

    # تتراوح تقييمات النموذج عادةً من 1 إلى 5
    rating = int(torch.argmax(probs).item() + 1)  # نضيف 1 لأن الفهارس تبدأ من 0
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