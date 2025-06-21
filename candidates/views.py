import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from .models import Candidate
from .forms import CandidateForm, UploadFileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def candidate_list(request):
    query = request.GET.get('q')
    candidates = Candidate.objects.filter(company=request.user)

    if query:
        candidates = candidates.filter(
            Q(name__icontains=query) |
            Q(college__icontains=query) |
            Q(course_title__icontains=query)
        )

    return render(request, 'candidates/candidate_list.html', {'candidates': candidates})

@login_required
def candidate_create(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.company = request.user
            candidate.save()
            messages.success(request, 'Candidate added successfully!')
            return redirect('candidate_list')
    else:
        form = CandidateForm()
    return render(request, 'candidates/candidate_form.html', {'form': form})

@login_required
def candidate_edit(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk, company=request.user)
    if request.method == 'POST':
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidate updated.')
            return redirect('candidate_list')
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'candidates/candidate_form.html', {'form': form})

@login_required
def candidate_delete(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk, company=request.user)
    if request.method == 'POST':
        candidate.delete()
        messages.success(request, 'Candidate deleted.')
        return redirect('candidate_list')
    return render(request, 'candidates/candidate_confirm_delete.html', {'candidate': candidate})


@login_required
def upload_candidates(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            required_columns = {'name', 'course_title', 'college', 'start_date', 'end_date', 'email', 'phone'}
            if not required_columns.issubset(df.columns):
                messages.error(request, f'Excel is missing required columns. Found: {df.columns}')
                return redirect('candidate_upload')

            for _, row in df.iterrows():
                try:
                    Candidate.objects.create(
                        company=request.user,
                        name=row['name'],
                        course_title=row['course_title'],
                        college=row['college'],
                        start_date=row['start_date'],
                        end_date=row['end_date'],
                        email=row['email'],
                        phone=str(row['phone']),
                    )
                except Exception as e:
                    messages.error(request, f"Error saving candidate: {e}")
            messages.success(request, 'Candidates uploaded successfully.')
            return redirect('candidate_list')
    else:
        form = UploadFileForm()
    return render(request, 'candidates/upload.html', {'form': form})
