import os
import contextlib
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from transformers import pipeline
from .forms import CourseSearchForm

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
    model = pipeline('text-generation', model='distilgpt2', truncation=True, max_new_tokens=200)

FILE_PATH = os.path.join(os.path.dirname(__file__), 'static', 'Upgrade.xlsx')

def get_course_and_university(points, data_for_model, field_of_study, institution_name):
    data_for_model.sort(key=lambda x: abs(float(x['POINTS']) - points))

    top_matches = data_for_model[:10]
    truncated_data_text = "\n".join([f"{record['PROGRAMME NAME']} ({record['PROGCODE']}) at {record['INSTITUTION NAME']} requires {record['POINTS']} points." for record in top_matches])

    data_text = f"Given {points} points, an interest in {field_of_study}, and a preference for {institution_name} institution, find the closest matching course and university:\n{truncated_data_text}\nBased on the above data, the closest match for {points} points in {field_of_study} at {institution_name} is:"

    response = model(data_text, num_return_sequences=1)
    return response[0]['generated_text']

def course_search_view(request):
    if request.method == 'POST':
       
        cluster_points = float(request.POST.get('cluster_points'))
        field_of_study = request.POST.get('field_of_study').lower()
        institution_name = request.POST.get('institution_name').lower()
                 
        df = pd.read_excel(FILE_PATH)
        df_latest = df[['INSTITUTION NAME', 'PROGRAMME NAME', 'PROGCODE', '2022']].dropna()
        df_latest.columns = ['INSTITUTION NAME', 'PROGRAMME NAME', 'PROGCODE', 'POINTS']
        df_latest = df_latest[df_latest['PROGRAMME NAME'].str.contains(field_of_study, case=False, na=False)]

        if institution_name:
            df_latest = df_latest[df_latest['INSTITUTION NAME'].str.contains(institution_name, case=False, na=False)]

        df_latest['POINTS'] = pd.to_numeric(df_latest['POINTS'], errors='coerce')
        df_latest = df_latest.dropna(subset=['POINTS'])

        data_for_model = df_latest.to_dict('records')

        results = []
        if data_for_model:
            match = get_course_and_university(cluster_points, data_for_model, field_of_study, institution_name)
            results = [{'progcode': record['PROGCODE'], 'program_name': record['PROGRAMME NAME'], 'institution_name': record['INSTITUTION NAME'], 'points_required': record['POINTS']} for record in data_for_model]

        return render(request, 'course_search.html', {'form': CourseSearchForm(), 'results': results})

    else:
        form = CourseSearchForm()

    return render(request, 'course_search.html', {'form': form, 'results': []})
