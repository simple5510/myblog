from .forms import LoginForm


# 设置全局模板变量

def login_modal_form(request):
    return {'login_modal_form': LoginForm()}
