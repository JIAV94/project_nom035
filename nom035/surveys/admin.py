from django.contrib import admin
from .models import *


admin.site.register(Survey)
admin.site.register(Section)
admin.site.register(Question)
admin.site.register(AnswerSheet)
admin.site.register(Answer)
admin.site.register(Grade)