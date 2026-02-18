from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.db.models import Count
from .models import Tournament, User
from participants.models import Participant
from .forms import TournamentForm
from .telegram_notify import send_tournament_to_telegram, delete_tournament_message

# --- CBV миксин для проверки группы ---
class OrganizerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Организаторы турниров").exists()

# --- CBV для создания турнира ---
class TournamentCreateView(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = Tournament
    form_class = TournamentForm
    template_name = "tournaments/create.html"
    success_url = reverse_lazy("tournament_history")

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)

# --- CBV для истории турниров (только свои) ---
class TournamentHistoryView(LoginRequiredMixin, OrganizerRequiredMixin, ListView):
    model = Tournament
    template_name = "tournaments/history.html"
    context_object_name = "tournaments"
    def get_queryset(self):
        return Tournament.objects.filter(organizer=self.request.user).order_by("-date").annotate(registeredCount = Count('participants'))

# --- CBV для редактирования турнира (только свои) ---
class TournamentUpdateView(LoginRequiredMixin, OrganizerRequiredMixin, UpdateView):
    model = Tournament
    form_class = TournamentForm
    template_name = "tournaments/edit.html"
    success_url = reverse_lazy("tournament_history")
    def get_queryset(self):
        return Tournament.objects.filter(organizer=self.request.user)

# --- CBV для удаления турнира (только свои) ---
class TournamentDeleteView(LoginRequiredMixin, OrganizerRequiredMixin, DeleteView):
    model = Tournament
    template_name = "tournaments/confirm_delete.html"
    success_url = reverse_lazy("tournament_history")

    def get_queryset(self):
        return Tournament.objects.filter(organizer=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        delete_tournament_message(obj)
        return super().delete(request, *args, **kwargs)

# --- FBV для участников ---
def join_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = request.user
    Participant.objects.get_or_create(tournament=tournament, user=user)
    return redirect('tournament_history')

def leave_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    user = request.user
    Participant.objects.filter(tournament=tournament, user=user).delete()
    return redirect('tournament_history')

def list_tournaments(request):
    # Например, действующие турниры — те, у кого status равен 'active'
    tournaments = Tournament.objects.filter(status='active')
    return render(request, "tournaments/list_tournaments.html", {"tournaments": tournaments})

def index(request):
    return render(request, "index.html")