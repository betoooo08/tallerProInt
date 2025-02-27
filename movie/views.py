from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
from django.db.models import Count

def statistics_view(request):
    matplotlib.use('Agg')
    
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {year: Movie.objects.filter(year=year).count() for year in years if year}
    
    if None in years:
        movie_counts_by_year["None"] = Movie.objects.filter(year__isnull=True).count()

    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_year))

    plt.figure(figsize=(10, 5))
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    graphic_years = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    all_movies = Movie.objects.values_list('genre', flat=True)
    
    genre_counts = {}
    for genres in all_movies:
        if genres:
            first_genre = genres.split(',')[0].strip()
            genre_counts[first_genre] = genre_counts.get(first_genre, 0) + 1

    sorted_genres = sorted(genre_counts.items())

    labels = [item[0] for item in sorted_genres]
    sizes = [item[1] for item in sorted_genres]

    plt.figure(figsize=(7, 7))
    wedges, texts, autotexts = plt.pie(
        sizes, labels=labels, autopct='%1.1f%%', colors=plt.cm.Paired.colors, startangle=140
    )

    for text, autotext in zip(texts, autotexts):
        text.set_fontsize(10)
        autotext.set_fontsize(9)

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    graphic_genres = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'statistics.html', {'graphic_years': graphic_years, 'graphic_genres': graphic_genres})