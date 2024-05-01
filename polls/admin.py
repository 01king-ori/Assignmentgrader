from django.contrib import admin

from .models import Lecturer
from .models import Assignment
from .models import Student
from .models import Submission
from .models import GradeReport,Course
admin.site.register(Lecturer)
admin.site.register(Assignment)
admin.site.register(Student)
admin.site.register(Submission)
admin.site.register(GradeReport)
admin.site.register(Course)

