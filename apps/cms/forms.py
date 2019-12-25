from apps.form import FormMixin
from django import forms
from apps.news.models import News, Banner
from apps.course.models import Course

class EditNewsCategoryForm(forms.Form, FormMixin):
    pk = forms.IntegerField(error_messages={
        'required': '必须传入分类的id！'
    })
    name = forms.CharField(max_length=32)

class WriteNewsForm(forms.ModelForm, FormMixin):
    # 因为category在模型中是外键而表单上是int，所有我们不能将其使用模型的验证
    category = forms.IntegerField()
    class Meta:
        model = News
        exclude = ['category', 'author', 'pub_time']

class EditNewsForm(forms.ModelForm,FormMixin):
    category = forms.IntegerField()
    pk = forms.IntegerField()
    class Meta:
        model = News
        exclude = ['category','author','pub_time']

class AddBannerForm(forms.ModelForm, FormMixin):
    class Meta:
        model = Banner
        fields = ('priority', 'link_to', 'image_url')

class EditBannerForm(forms.ModelForm, FormMixin):
    # 主键id不能写在fields中，因为在Banner模型中没用自己定义主键id，
    # 如果你在fields加上id跟没加一样不会起作用
    # 注意：在这里最好不要写成id，因为id是Python的内置函数，避免混淆
    pk = forms.IntegerField()
    class Meta:
        model = Banner
        fields = ('priority', 'link_to', 'image_url')

class PubCourseForm(forms.ModelForm,FormMixin):
    category_id = forms.IntegerField()
    teacher_id = forms.IntegerField()
    class Meta:
        model = Course
        exclude = ("category", 'teacher')
