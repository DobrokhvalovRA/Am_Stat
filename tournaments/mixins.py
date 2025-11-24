from django.contrib.auth.mixins import UserPassesTestMixin

class OrganizerRequiredMixin(UserPassesTestMixin):
    """
    Доступ только пользователям из группы 'Организаторы турниров'
    """
    def test_func(self):
        return self.request.user.groups.filter(name="Организаторы турниров").exists()