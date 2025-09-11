from PIL import Image
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductAuction

# متغير عالمي لتخزين النموذج بعد تحميله لأول مرة
MODEL = None

def get_model():
    """تحميل النموذج عند الحاجة فقط (Lazy Loading)."""
    global MODEL
    if MODEL is None:
        MODEL = SentenceTransformer('clip-ViT-B-32')
    return MODEL

def get_image_embedding(image_input):
    """
    دالة لحساب embedding من صورة.
    إذا تم تمرير مسار للصورة (str) يتم فتحها مباشرة،
    وإذا تم تمرير كائن ملف يتم استخدامه مباشرة.
    """
    if isinstance(image_input, str):
        image = Image.open(image_input).convert('RGB')
    else:
        image = Image.open(image_input).convert('RGB')
    
    model = get_model()
    embedding = model.encode([image])[0]
    return embedding


def build_faiss_index():
    """
    هذه الدالة تقرأ صور المنتجات من جدول Product وجدول ProductAuction،
    وتجميعها في قائمة واحدة مع بيانات إضافية؛ ثم تحسب الـ embedding لكل صورة
    وتبني فهرس FAISS باستخدام المسافة الإقليدية (L2).
    """
    all_items = []
    
    # جلب منتجات المتجر
    products = Product.objects.all()
    for product in products:
        # نفترض أن حقل الصورة في نموذج Product اسمه image (ImageField)
        if product.image:
            all_items.append(product)
    
    # جلب منتجات المزاد
    auction_products = ProductAuction.objects.all()
    for auction in auction_products:
        if auction.image:
            all_items.append(auction)
    
    # حساب الـ embeddings لكل صورة
    embeddings = []
    for item in all_items:
        try:
            emb = get_image_embedding(item.image.path)
            embeddings.append(emb)
        except Exception as e:
            # يمكنك تسجيل الأخطاء أو تجاهل الصور التي لم يتمكن من فتحها
            print(f"Error processing {item.image.path}: {e}")
            continue

    embeddings = np.array(embeddings).astype('float32')
    
    # بناء فهرس FAISS
    if embeddings.size == 0:
        raise ValueError("لم يتم الحصول على أي embeddings!")
    d = embeddings.shape[1]  # عدد أبعاد الـ embedding
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    
    return index, all_items

# بناء الفهرس عند بدء تشغيل التطبيق وحفظه في متغيرات عالمية لتجنب إعادة البناء في كل طلب.
FAISS_INDEX = None
ALL_ITEMS = []

def get_faiss_index():
    global FAISS_INDEX, ALL_ITEMS
    if FAISS_INDEX is None or not ALL_ITEMS:
        try:
            FAISS_INDEX, ALL_ITEMS = build_faiss_index()
        except ValueError as e:
            print(f"⚠️ FAISS index error: {e}")
            FAISS_INDEX, ALL_ITEMS = None, []
    return FAISS_INDEX, ALL_ITEMS


def search_similar_products(query_image, distance_threshold=60):
    """
    تقوم هذه الدالة بتحويل صورة البحث إلى embedding ثم تبحث في الفهرس عن الصور
    التي تكون مسافتها أقل من العتبة المحددة.
    تُرجع الدالة النتائج على شكل قائمة من الكائنات (Product أو ProductAuction).
    """
    index, items = get_faiss_index()
    if not index:
        return []
    
    query_embedding = get_image_embedding(query_image)
    query_embedding = np.array([query_embedding]).astype('float32')
    D, I = index.search(query_embedding, len(items))
    
    result_items = [items[idx] for dist, idx in zip(D[0], I[0]) if dist < distance_threshold]
    return result_items


# ربط إعادة بناء الفهرس باستخدام Django signals عند حفظ أو تعديل الكائنات
@receiver(post_save, sender=Product)
@receiver(post_save, sender=ProductAuction)
def rebuild_faiss_index(sender, instance, **kwargs):
    """
    إشارة Django لإعادة بناء فهرس FAISS بعد حفظ أو تعديل كائن من نموذج Product
    أو ProductAuction.
    """
    global FAISS_INDEX, ALL_ITEMS
    try:
        FAISS_INDEX, ALL_ITEMS = build_faiss_index()
    except ValueError as e:
        FAISS_INDEX, ALL_ITEMS = None, []
