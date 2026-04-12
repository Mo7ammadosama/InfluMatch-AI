#!/usr/bin/env python3
"""Seed RAG vector store — contracts, policies, Jordan market docs"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent / "influmatch"
sys.path.insert(0, str(ROOT))

ARABIC_CONTRACT = """
عقد تعاون تسويقي بالمؤثرين
بين: التاجر (الطرف الأول) والمؤثر (الطرف الثاني)

البند الأول: موضوع العقد
يلتزم الطرف الثاني بتنفيذ المهام التسويقية المحددة في الملحق (أ)
خلال المدة المتفق عليها وبالمواصفات المطلوبة.

البند الثاني: المقابل المالي
يلتزم الطرف الأول بدفع المبلغ المتفق عليه بالدينار الأردني (JOD)
عبر نظام الضمان المالي (Escrow) في منصة InfluMatch.jo.
يطبق ضريبة القيمة المضافة بنسبة 16% وفق التشريع الأردني.

البند الثالث: التسليمات المطلوبة
يجب أن تتضمن المحتوى المتفق عليه (منشور/قصة/ريل)
مع ذكر العلامة التجارية والهاشتاقات المحددة.

البند الرابع: حقوق الملكية الفكرية
يحتفظ الطرف الأول بحق استخدام المحتوى المنتج لمدة 12 شهراً.

البند الخامس: فض النزاعات
تحال النزاعات إلى فريق InfluMatch.jo خلال 48 ساعة من نشوئها.
القانون الواجب التطبيق: القانون الأردني.
"""

ENGLISH_CONTRACT = """
Influencer Marketing Collaboration Agreement
Between: Merchant (Party A) and Influencer (Party B)

Article 1: Scope of Work
Party B agrees to execute the marketing deliverables specified in Appendix A
within the agreed timeline and to the specified quality standards.

Article 2: Compensation
Party A agrees to pay the agreed amount in Jordanian Dinar (JOD)
through the InfluMatch.jo Escrow system.
VAT at 16% applies per Jordan tax law.

Article 3: Deliverables
Must include agreed content types (post/story/reel)
with brand mentions and specified hashtags.

Article 4: Intellectual Property
Party A retains rights to produced content for 12 months.

Article 5: Dispute Resolution
Disputes escalated to InfluMatch.jo within 48 hours.
Governing law: Hashemite Kingdom of Jordan.
"""

JORDAN_POLICY = """
سياسات منصة InfluMatch.jo — السوق الأردني

1. سياسة الدفع والضمان المالي (Escrow):
- يتم تجميد المبلغ في حساب الضمان فور إطلاق الحملة
- يحرر المبلغ تلقائياً بعد 7 أيام من الموافقة على المحتوى
- عمولة المنصة: 5% من إجمالي قيمة الحملة
- ضريبة القيمة المضافة: 16% وفق قانون ضريبة المبيعات الأردني

2. معايير المحتوى في السوق الأردني:
- يجب احترام القيم والثقافة الأردنية في جميع المحتويات
- يحظر المحتوى المسيء دينياً أو اجتماعياً
- يجب الإفصاح عن الطابع الإعلاني للمحتوى

3. سياسة النزاعات:
- مدة تقديم النزاع: 48 ساعة من تسليم المحتوى
- يقوم الذكاء الاصطناعي ARIA بمراجعة أولية للنزاع

4. معايير المؤثرين:
- الحد الأدنى للمتابعين: 1,000 متابع على أي منصة
- درجة ARIA Score مطلوبة: لا تقل عن 40 نقطة

5. سياسة إلغاء الحملات:
- الإلغاء قبل 48 ساعة: استرداد كامل للمبلغ
- الإلغاء بعد بدء التنفيذ: استرداد 50% فقط
- الإلغاء بعد التسليم: لا يحق استرداد المبلغ
"""

def seed():
    from backend.services.rag.vector_store import InfluMatchVectorStore
    store = InfluMatchVectorStore()

    store.ingest_document(ARABIC_CONTRACT, "contracts",
        {"id": "template_ar_001", "language": "ar", "source": "InfluMatch Contract Template AR"})
    store.ingest_document(ENGLISH_CONTRACT, "contracts",
        {"id": "template_en_001", "language": "en", "source": "InfluMatch Contract Template EN"})
    store.ingest_document(JORDAN_POLICY, "policies",
        {"id": "jordan_platform_policy", "language": "ar", "source": "InfluMatch Platform Policy v1.0"})

    print("[RAG] Contract templates seeded (AR + EN)")
    print("[RAG] Platform policies seeded")
    print("[RAG] Knowledge base ready")

if __name__ == "__main__":
    print("[ARIA] Seeding RAG Knowledge Base...")
    seed()
    print("[ARIA] RAG seeding complete")
