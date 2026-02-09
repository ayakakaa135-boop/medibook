# تقرير تنفيذ نظام الترجمة

## المقدمة

يهدف هذا التقرير إلى توثيق عملية إضافة نظام الترجمة إلى مشروع MediBook، مما يتيح ترجمة البيانات الموجودة في قاعدة البيانات إلى اللغة العربية. تم استخدام مكتبة `django-modeltranslation` لتسهيل هذه العملية، بالإضافة إلى تطوير أداة مساعدة لترجمة البيانات الحالية باستخدام نموذج لغوي كبير (LLM).

## الخطوات المنفذة

تم تنفيذ الخطوات التالية لإضافة دعم الترجمة:

### 1. فحص المشروع وتحديد النماذج

تم فحص بنية المشروع وتحديد النماذج (Models) التي تحتوي على حقول تتطلب الترجمة. النماذج المستهدفة هي:

*   **Clinic**: `name`, `description`, `address`, `city`
*   **Specialization**: `name`, `description`
*   **Doctor**: `education`, `bio`
*   **Service**: `name`, `description`, `preparation_instructions`

### 2. إعداد `django-modeltranslation`

تم التأكد من تثبيت `django-modeltranslation` وتكوينه في ملف `config/settings.py`:

*   تمت إضافة `modeltranslation` إلى `INSTALLED_APPS`.
*   تمت إضافة `django.middleware.locale.LocaleMiddleware` إلى `MIDDLEWARE`.
*   تم تعريف `LANGUAGES` لدعم اللغتين العربية (`ar`) والإنجليزية (`en`).

### 3. إنشاء ملفات `translation.py`

لكل تطبيق يحتوي على نماذج قابلة للترجمة، تم إنشاء ملف `translation.py` داخل مجلد التطبيق. تحدد هذه الملفات الحقول التي يجب ترجمتها لكل نموذج:

*   **`apps/clinics/translation.py`**:
    ```python
    from modeltranslation.translator import register, TranslationOptions
    from .models import Clinic

    @register(Clinic)
    class ClinicTranslationOptions(TranslationOptions):
        fields = (
            'name',
            'description',
            'address',
            'city'
        )
    ```

*   **`apps/doctors/translation.py`**:
    ```python
    from modeltranslation.translator import register, TranslationOptions
    from .models import Specialization, Doctor

    @register(Specialization)
    class SpecializationTranslationOptions(TranslationOptions):
        fields = (
            'name',
            'description'
        )

    @register(Doctor)
    class DoctorTranslationOptions(TranslationOptions):
        fields = (
            'education',
            'bio'
        )
    ```

*   **`apps/services/translation.py`**:
    ```python
    from modeltranslation.translator import register, TranslationOptions
    from .models import Service

    @register(Service)
    class ServiceTranslationOptions(TranslationOptions):
        fields = (
            'name',
            'description',
            'preparation_instructions'
        )
    ```

### 4. تحديث متطلبات Python

تم تعديل ملف `pyproject.toml` لتغيير متطلب إصدار Python من `>=3.12` إلى `>=3.11` ليتوافق مع بيئة التشغيل.

### 5. تثبيت التبعيات

تم تثبيت جميع تبعيات المشروع، بما في ذلك `django-modeltranslation`، باستخدام `pip3`.

### 6. إنشاء وتطبيق التهجيرات (Migrations)

بعد تحديد الحقول القابلة للترجمة، تم إنشاء تهجيرات جديدة لقاعدة البيانات لإضافة الحقول المترجمة (مثل `name_ar`, `name_en`, إلخ) إلى النماذج المعنية. تم تطبيق هذه التهجيرات على قاعدة البيانات:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

ملاحظة: تم التبديل مؤقتًا إلى قاعدة بيانات SQLite لتوليد التهجيرات محليًا، ثم العودة إلى PostgreSQL.

### 7. تطوير أمر ترجمة البيانات

تم إنشاء أمر إدارة مخصص (`translate_data`) في `apps/core/management/commands/translate_data.py` لترجمة البيانات الموجودة في قاعدة البيانات تلقائيًا إلى اللغة العربية باستخدام نموذج لغوي كبير (LLM). يستخدم هذا الأمر OpenAI API للترجمة.

```python
# apps/core/management/commands/translate_data.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.clinics.models import Clinic
from apps.doctors.models import Doctor, Specialization
from apps.services.models import Service
from openai import OpenAI

class Command(BaseCommand):
    help = 'Translate existing database data to Arabic using LLM'

    def handle(self, *args, **kwargs):
        client = OpenAI()
        
        self.stdout.write('Translating Specializations...')
        for obj in Specialization.objects.all():
            if not obj.name_ar:
                obj.name_ar = self.translate(client, obj.name)
            if not obj.description_ar and obj.description:
                obj.description_ar = self.translate(client, obj.description)
            obj.save()

        self.stdout.write('Translating Clinics...')
        for obj in Clinic.objects.all():
            if not obj.name_ar:
                obj.name_ar = self.translate(client, obj.name)
            if not obj.description_ar:
                obj.description_ar = self.translate(client, obj.description)
            if not obj.address_ar:
                obj.address_ar = self.translate(client, obj.address)
            if not obj.city_ar:
                obj.city_ar = self.translate(client, obj.city)
            obj.save()

        self.stdout.write('Translating Doctors...')
        for obj in Doctor.objects.all():
            if not obj.education_ar and obj.education:
                obj.education_ar = self.translate(client, obj.education)
            if not obj.bio_ar and obj.bio:
                obj.bio_ar = self.translate(client, obj.bio)
            obj.save()

        self.stdout.write('Translating Services...')
        for obj in Service.objects.all():
            if not obj.name_ar:
                obj.name_ar = self.translate(client, obj.name)
            if not obj.description_ar:
                obj.description_ar = self.translate(client, obj.description)
            if not obj.preparation_instructions_ar and obj.preparation_instructions:
                obj.preparation_instructions_ar = self.translate(client, obj.preparation_instructions)
            obj.save()

        self.stdout.write(self.style.SUCCESS('Successfully translated data'))

    def translate(self, client, text):
        if not text:
            return ""
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a professional medical translator. Translate the following text to Arabic. Return only the translation."},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error translating '{text}': {e}"))
            return text
```

### 8. إضافة `apps.core` إلى `INSTALLED_APPS`

لضمان اكتشاف أمر الإدارة الجديد، تم إضافة `apps.core` إلى `INSTALLED_APPS` في `config/settings.py`.

### 9. تحديث لوحة تحكم الإدارة

تم تعديل ملفات `admin.py` في تطبيقات `clinics`, `doctors`, و `services` لاستخدام `TranslationAdmin` بدلاً من `admin.ModelAdmin`. هذا يوفر واجهة مستخدم محسنة في لوحة تحكم Django Admin لإدارة الترجمات مباشرة.

## كيفية استخدام الترجمة

1.  **تشغيل أمر الترجمة**: لترجمة البيانات الموجودة في قاعدة البيانات، قم بتشغيل الأمر التالي:
    ```bash
    python3 manage.py translate_data
    ```
2.  **إدارة الترجمات في لوحة التحكم**: بعد تطبيق التغييرات، يمكنك الوصول إلى لوحة تحكم Django Admin (عادةً على `/admin/`) وستجد حقول الترجمة (مثل `Name (Arabic)`, `Name (English)`) متاحة للتحرير لكل نموذج تم تكوينه.
3.  **عرض المحتوى المترجم في القوالب**: يمكنك استخدام علامات القالب (`{% language 'ar' %}` أو `{% language 'en' %}`) لعرض المحتوى باللغة المطلوبة في قوالب Django.

## الخلاصة

تم بنجاح دمج نظام الترجمة في مشروع MediBook، مما يوفر القدرة على تخزين وإدارة وعرض البيانات بلغات متعددة، مع التركيز على اللغة العربية. يمكن للمسؤولين الآن ترجمة المحتوى بسهولة من خلال لوحة تحكم الإدارة، ويمكن للمطورين استخدام الحقول المترجمة في القوالب الخاصة بهم.
