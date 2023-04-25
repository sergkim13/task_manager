from typing import Any, Callable

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import ProtectedError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import DeleteView

from .constants import MSG_NO_PERMISSION, REVERSE_HOME, REVERSE_LOGIN


class AuthentificationPermissionMixin(LoginRequiredMixin):
    '''Sets access rules for unauthenticated users.'''

    def handle_no_permission(self) -> HttpResponseRedirect:
        '''Sets rules when a page is unavailable to an unauthenticated user.'''
        messages.warning(self.request, MSG_NO_PERMISSION)
        return redirect(REVERSE_LOGIN)


class ModifyPermissionMixin(LoginRequiredMixin):
    '''Sets access rules for an unauthorized user.'''

    unpermission_message: str = 'Access denied message'
    unpermission_url: str | Callable[..., Any] = REVERSE_LOGIN

    def dispatch(self, request: HttpRequest,
                 *args: Any, **kwargs: Any) -> HttpResponse:
        '''Specifies access settings for the current user.
        Provides access if the user is authenticated.'''
        if request.user.id != self.get_object().id:
            messages.error(self.request, self.unpermission_message)
            return redirect(self.unpermission_url)
        return super().dispatch(request, *args, **kwargs)


class DeletionProtectionMixin(DeleteView):
    '''Sets the rules for handling the case of the impossibility of deleting data
    due to the protection of related data.'''

    protected_data_message: str = 'Entity deletion forbidden message'
    protected_data_url: str | Callable[..., Any] = REVERSE_HOME

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        '''Sends data to the server with protection check.'''
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(self.request, self.protected_data_message)
            return redirect(self.protected_data_url)


class TaskDeletionPermissionMixin(LoginRequiredMixin):
    unpermission_message: str = 'Task deletion forbidden message'
    unpermission_url: str = 'redirected_url'

    def dispatch(self, request, *args, **kwargs):
        '''Provides access for task deletion if the user is task's author.'''
        if request.user.id != self.get_object().author.id:
            if request.user.is_authenticated:
                messages.error(self.request, self.unpermission_message)
            return redirect(self.unpermission_url)
        return super().dispatch(request, *args, **kwargs)
