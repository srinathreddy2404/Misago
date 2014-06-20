from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from misago.admin.views import generic
from misago.users.forms.admin import (StaffFlagUserFormFactory, NewUserForm,
                                      EditUserForm)


class UserAdmin(generic.AdminBaseMixin):
    root_link = 'misago:admin:users:accounts:index'
    templates_dir = 'misago/admin/users'

    def get_model(self):
        return get_user_model()

    def create_form_type(self, request, target):
        return StaffFlagUserFormFactory(
            self.Form, target, add_staff_field=request.user.is_superuser)


class UsersList(UserAdmin, generic.ListView):
    items_per_page = 20
    ordering = (
        ('-id', _("From newest")),
        ('id', _("From oldest")),
        ('username', _("A to z")),
        ('-username', _("Z to a")),
        )


class NewUser(UserAdmin, generic.ModelFormView):
    Form = NewUserForm
    template = 'new.html'
    message_submit = _('New user "%s" has been registered.')

    def handle_form(self, form, request, target):
        User = get_user_model()
        new_user = User.objects.create_user(
            form.cleaned_data['username'],
            form.cleaned_data['email'],
            form.cleaned_data['new_password'],
            title=form.cleaned_data['title'],
            rank=form.cleaned_data.get('rank'))

        if form.cleaned_data.get('staff_level'):
            new_user.staff_level = form.cleaned_data['staff_level']

        if form.cleaned_data.get('roles'):
            new_user.roles.add(*form.cleaned_data['roles'])

        new_user.update_acl_token()
        new_user.save()

        messages.success(request, self.message_submit % target.username)
        return redirect('misago:admin:users:accounts:edit',
                        user_id=new_user.pk)


class EditUser(UserAdmin, generic.ModelFormView):
    Form = EditUserForm
    template = 'edit.html'
    message_submit = _('User "%s" has been edited.')

    def handle_form(self, form, request, target):
        form.instance.save()

        if form.cleaned_data.get('staff_level'):
            form.instance.staff_level = form.cleaned_data['staff_level']

        if form.cleaned_data.get('roles'):
            form.instance.roles.add(*form.cleaned_data['roles'])

        form.instance.update_acl_token()
        form.instance.save()

        messages.success(request, self.message_submit % target.username)