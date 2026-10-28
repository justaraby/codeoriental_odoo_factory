# Smart Factory Operating System (OS) | نظام المصنع الذكي المتكامل لأودو
> **Turnkey Factory ERP for Odoo 17, 18, 19 & 20 — Zero Consultant Needed**  
> **Price: €65.00** | **License: OPL-1** | **Author: CodeOriental**

---

## 📖 نظرة عامة | Overview

**Smart Factory OS** هو موديول متكامل وقوي مصمم لتحويل نظام أودو (سواء على Odoo.sh أو السيرفر الخاص On-Premise) إلى نظام تشغيل مصانع متكامل فور التثبيت، **بدون الحاجة إلى خبير أو استشاري أودو**.

يوفر النظام واجهة مركزية موحدة، معالج تهيئة ذكي يبني خطوط الإنتاج والورديات ومعايير الهالك في 60 ثانية، واجهة صالة إنتاج مبسطة لشاشات اللمس للمشغلين، ومحرك لحساب التكلفة الحقيقية (خامات + عمالة + ماكينات وكهرباء + مصاريف تشغيل غير مباشرة) وهامش الربح الفعلي لكل تشغيلة.

---

## 🌟 الميزات الجوهرية | Key Features

1. **معالج التهيئة الذكي (Factory Quick Setup Wizard)**:
   - اختيار نشاط المصنع بنقرة واحدة من بين 8 أنشطة جاهزة (أغذية ومخابز، بلاستيك وحقن، معادن وخراطة CNC، ملابس ومنسوجات، كيماويات ومنظفات، أخشاب وأثاث، إلكترونيات وتجميع، ورش وتصنيع عام).
   - بناء خطوط الإنتاج ومراكز العمل مع تكلفتها بالساعة وطاقتها الإنتاجية تلقائياً.
   - تهيئة الورديات (وردية، ورديتين، أو 3 ورديات 24/7).
   - إنشاء خامات تجريبية ومنتج نهائي مع قائمة مواد (BOM) ومراحل تشغيل جاهزة للاختبار الفوري.

2. **مركز قيادة المصنع الموحد (Plant Command Center Dashboard)**:
   - مراقبة حية لسرعة الإنتاج والكميات المنتجة اليوم مقابل المستهدف.
   - كفاءة وتوفر الخطوط والماكينات (OEE) والماكينات المتوقفة.
   - تنبيهات فورية لنواقص المواد الخام في المخزن باللون الأحمر.
   - تنبيهات تجاوز نسبة الهالك (Scrap Alert) المحددة.
   - أزرار وصول سريع لإطلاق التشغيلات وطلب الخامات والإبلاغ عن الأعطال.

3. **واجهة المشغلين المبسطة لصالة الإنتاج (Shopfloor Tablet Kiosk)**:
   - شاشة لمس مخصصة لعمال ومشرفي الخطوط بأزرار واضحة ومبسطة.
   - إنجاز التشغيلة وتسجيل الإنتاج بنقرة واحدة (1-Click Complete) دون المرور بتعقيدات أودو.

4. **حاسبة التكلفة الحقيقية والربحية للتشغيلة (4-Pillar Batch Costing & Profit Engine)**:
   - حساب فوري للتكلفة المباشرة وغير المباشرة:
     1. تكلفة الخامات المستهلكة فعلياً.
     2. تكلفة عمالة التشغيل (ساعات المشغلين × الأجر).
     3. تكلفة تشغيل الماكينة واستهلاك الطاقة والكهرباء.
     4. نسبة المصاريف الصناعية غير المباشرة (Factory Overhead).
   - حساب التكلفة الحقيقية للقطعة (Unit Cost).
   - اقتراح الحد الأدنى لسعر البيع لتحقيق هامش الربح المستهدف.
   - عرض هامش الربح الفعلي مقارنة بسعر قائمة البيع.

5. **أذونات صرف ومراقبة نواقص الخامات (Smart Material Requisitions)**:
   - إنشاء إذن صرف خامات آلياً من أمر الإنتاج.
   - فحص توفر الخامات في المخزن، وإبراز العجز باللون الأحمر.
   - زر بنقرة واحدة لإنشاء طلب شراء (Purchase RFQ) فوري لمسؤولي المشتريات.

6. **مراقبة الماكينات وسجل الأعطال والتوقف (Machinery & Downtime Logs)**:
   - بطاقات ملونة لحالة الماكينات (تعمل، في الانتظار، صيانة، معطلة).
   - إبلاغ فوري عن العطل مع تسجيل السبب والوقت وحساب التكلفة المفقودة.

7. **مستندات تشغيل مصنع احترافية مع باركود (Printable Documents)**:
   - بطاقة تشغيل وأمر إنتاج بصري مع باركود Code128 وتوقيعات الاستلام والجودة.
   - إذن صرف خامات معتمد لأمناء المخازن.
   - كشف تحليلي لتكاليف وهوامش ربح التشغيلة.

---

## 🗂️ هيكل الموديول | Module Structure

```text
smart_factory_os/
├── __init__.py
├── __manifest__.py
├── LICENSE                       # OPL-1 License
├── data/
│   ├── factory_sequence.xml       # Sequences for batches, downtimes, shifts, requisitions
│   └── factory_industry_templates_data.xml # 8 pre-configured industry profiles
├── models/
│   ├── __init__.py
│   ├── factory_industry_template.py # Industry presets & work centers
│   ├── factory_machine.py          # Machinery, equipment & downtime incident logs
│   ├── factory_shift.py            # Shift schedules & daily handover logs
│   ├── factory_material_requisition.py # Material requisition & shortage handling
│   ├── factory_production.py       # MRP Production 4-pillar costing & shopfloor extensions
│   ├── factory_cost_analysis.py    # Analytical SQL view for batch profitability
│   └── factory_dashboard.py        # Plant Command Center KPIs & shortcuts
├── report/
│   ├── factory_reports.xml         # Report actions
│   ├── report_batch_traveler.xml   # Batch traveler job card with Code128 barcode
│   ├── report_material_requisition.xml # Raw material requisition slip
│   └── report_cost_analysis.xml    # Batch cost absorption sheet
├── security/
│   ├── factory_security.xml        # User groups (Operator, Supervisor, Manager) & multi-company rules
│   └── ir.model.access.csv         # Full model access rights
├── static/
│   ├── description/
│   │   ├── icon.png                # App icon (256x256)
│   │   ├── banner.png              # App store showcase banner (1376x768)
│   │   ├── screenshot_dashboard.png# Command Center showcase
│   │   ├── screenshot_wizard.png   # Setup Wizard showcase
│   │   └── index.html              # High-converting responsive App Store presentation
│   └── src/
│       └── scss/
│           └── factory_theme.scss  # Styling enhancements
└── wizard/
    ├── __init__.py
    ├── factory_onboarding_wizard.py # Zero-consultant automated deployment engine
    ├── factory_quick_run_wizard.py  # Instant 10-second batch launcher
    └── factory_downtime_wizard.py   # Operator machine breakdown reporter
```

---

## 🌿 الفروع وتوافق الإصدارات | Git Branches & Version Compatibility

تم تجهيز المستودع ليحتوي على فروع مستقلة لكل إصدار رئيسي من أودو:

| Branch | Odoo Version | Manifest Version | Status |
|:---:|:---:|:---:|:---:|
| `17.0` | Odoo 17.0 (LTS) | `17.0.1.0.0` | ✅ جاهز للنشر |
| `18.0` | Odoo 18.0 (Current) | `18.0.1.0.0` | ✅ جاهز للنشر |
| `19.0` | Odoo 19.0 (Future) | `19.0.1.0.0` | ✅ جاهز للنشر |
| `20.0` | Odoo 20.0 (Roadmap) | `20.0.1.0.0` | ✅ جاهز للنشر |

---

## 🚀 كيفية الرفع على GitHub وربطه بمتجر تطبيقات أودو | Deployment Guide

### 1. إنشاء مستودع جديد على GitHub:
- توجه إلى [GitHub](https://github.com/new).
- قم بإنشاء مستودع جديد باسم، مثلاً: `smart_factory_os` أو `codeoriental_odoo_factory`.
- اجعل المستودع عاماً (Public) أو خاصاً (Private) مع منح صلاحية لصانع متجر أودو.

### 2. ربط المستودع المحلي بالـ Remote ورفع الفروع:
افتح الطرفية (Terminal / PowerShell) داخل مجلد المشروع ونفذ:

```bash
# ربط المستودع برابط GitHub الخاص بك
git remote add origin https://github.com/YOUR_USERNAME/codeoriental_odoo_factory.git

# رفع الفرع الرئيسي وكل فروع الإصدارات دفعة واحدة
git push -u origin 17.0
git push -u origin 18.0
git push -u origin 19.0
git push -u origin 20.0
git push -u origin main
```

### 3. رفع الموديول على متجر تطبيقات أودو (apps.odoo.com):
1. سجل دخولك على [متجر تطبيقات أودو](https://apps.odoo.com).
2. اضغط على حسابك في الأعلى ثم اختر **My Modules / Register a Repository**.
3. أدخل رابط مستودع GitHub الخاص بك:
   `https://github.com/YOUR_USERNAME/codeoriental_odoo_factory`
4. سيقوم محرك فحص متجر أودو بفحص الفروع تلقائياً:
   - سيقرأ فرع `17.0` ويعرضه لمستخدمي أودو 17.
   - سيقرأ فرع `18.0` ويعرضه لمستخدمي أودو 18.
   - سيقرأ فرع `19.0` و `20.0` عند صدورها.
5. سيقرأ المتجر السعر المحدد في الـ Manifest:
   - **السعر**: `65.00 EUR`
   - **الترخيص**: `OPL-1` (ترخيص التطبيقات المدفوعة في متجر أودو)
   - **الأيقونة والبانر والوصف**: ستظهر تلقائياً بشكل فائق الجودة من مجلد `static/description/`.

---

## 💻 بيئات العمل المدعومة | Supported Environments

- **Odoo.sh**: يتم دعم الموديول بنسبة 100%، يكفي إضافة الفرع في مستودع مشروعك على odoo.sh.
- **On-Premise (Linux / Windows / Docker)**: ضع مجلد `smart_factory_os` داخل مسار الـ `addons_path` في ملف `odoo.conf` وقم بتحديث قائمة التطبيقات.
- **Odoo Community & Enterprise**: يعمل بسلاسة على النسختين المجانية والمدفوعة.

---

## 📞 الدعم الفني والتواصل | Support

- **الجهة المطورة**: CodeOriental
- **الموقع الإلكتروني**: [https://codeoriental.com](https://codeoriental.com)
- **البريد الإلكتروني**: support@codeoriental.com
