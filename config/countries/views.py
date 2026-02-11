from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count
from .models import Country


class CountryListView(ListView):
    model = Country
    template_name = 'countries/list.html'
    context_object_name = 'countries'
    paginate_by = 20

    def get_queryset(self):
        queryset = Country.objects.all()
        
        # Filtre par région
        region = self.request.GET.get('region')
        if region:
            queryset = queryset.filter(region=region)
        
        # Recherche par nom
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(common_name__icontains=search) | 
                Q(official_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Liste des régions pour le filtre
        context['regions'] = Country.objects.values_list('region', flat=True).distinct().order_by('region')
        
        # Paramètres actuels pour conserver les filtres dans la pagination
        context['current_region'] = self.request.GET.get('region', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context



class CountryDetailView(DetailView):
    model = Country
    template_name = 'countries/detail.html'
    context_object_name = 'country'



class StatsView(TemplateView):
    template_name = "countries/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_countries"] = Country.objects.count()

        context["top_population"] = Country.objects.order_by("-population")[:10]

        context["top_area"] = Country.objects.filter(
            area__isnull=False
        ).order_by("-area")[:10]

        context["region_distribution"] = (
            Country.objects
            .values("region")
            .annotate(count=Count("cca3"))
            .order_by("-count")
        )

        return context