from django.shortcuts import render, redirect
from .models import Expense
from .ml.auto_category import predict_category
from django.utils import timezone
import joblib
import os
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.shortcuts import render
from .models import Expense
from django.db.models.functions import TruncMonth
from django.db.models import Sum

from django.contrib.auth.decorators import login_required

# Load the model and vectorizer
model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'model.pkl')
vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'ml_model', 'vectorizer.pkl')

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)


from datetime import datetime
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from .models import Expense

from django.db.models import Q  # for flexible search

from datetime import datetime

@login_required
def home(request):
    category = request.GET.get('category')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('q')

    # ✅ New: Date Range Filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    expenses = Expense.objects.filter(user=request.user)

    if category and category != "All":
        expenses = expenses.filter(category=category)

    if search_query:
        expenses = expenses.filter(
            Q(description__icontains=search_query)
        )

    if start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            expenses = expenses.filter(date__range=[start_date_obj, end_date_obj])
        except ValueError:
            pass  # Handle invalid dates silently

    # Sorting
    if sort_by == 'amount_desc':
        expenses = expenses.order_by('-amount')
    elif sort_by == 'amount_asc':
        expenses = expenses.order_by('amount')
    elif sort_by == 'date_asc':
        expenses = expenses.order_by('date')
    else:
        expenses = expenses.order_by('-date')

    # Analytics
    total_spent = sum(exp.amount for exp in expenses)
    categories = Expense.objects.values_list('category', flat=True).distinct()

    monthly_data = (
        expenses
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    pie_data = (
        expenses
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    labels = [entry['month'].strftime("%b %Y") for entry in monthly_data]
    data = [entry['total'] for entry in monthly_data]
    pie_labels = [entry['category'] for entry in pie_data]
    pie_values = [entry['total'] for entry in pie_data]

    return render(request, 'index.html', {
        'expenses': expenses,
        'total_spent': total_spent,
        'categories': categories,
        'selected_category': category or "All",
        'selected_sort': sort_by or 'date_desc',
        'search_query': search_query or '',
        'start_date': start_date or '',
        'end_date': end_date or '',
        'labels': labels,
        'data': data,
        'pie_labels': pie_labels,
        'pie_data': pie_values
    })


@login_required
def add_expense(request):
    if request.method == 'POST':
        description = request.POST['description']
        amount = request.POST['amount']

        # Predict category using ML model
        vector = vectorizer.transform([description])
        predicted_category = model.predict(vector)[0]

        # Save to DB
        Expense.objects.create(
             user=request.user,
            description=description,
            amount=amount,
            category=predicted_category,
            date=timezone.now()
        )
        return redirect('expense_list')  # or update with correct route name

    return render(request, 'add_expense.html')
from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from django.utils import timezone
@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.description = request.POST['description']
        expense.amount = request.POST['amount']
        expense.date = request.POST['date']
        expense.save()
        return redirect('expense_list')
    return render(request, 'edit_expense.html', {'expense': expense})
@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('expense_list')
import csv
from django.http import HttpResponse
@login_required
def export_expenses_csv(request):
    category = request.GET.get('category')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('q')

    expenses = Expense.objects.filter(user=request.user)

    if category and category != "All":
        expenses = expenses.filter(category=category)

    if search_query:
        expenses = expenses.filter(description__icontains=search_query)

    if sort_by == 'amount_desc':
        expenses = expenses.order_by('-amount')
    elif sort_by == 'amount_asc':
        expenses = expenses.order_by('amount')
    elif sort_by == 'date_asc':
        expenses = expenses.order_by('date')
    else:
        expenses = expenses.order_by('-date')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=expenses.csv'

    writer = csv.writer(response)
    writer.writerow(['Description', 'Amount', 'Category', 'Date'])

    for expense in expenses:
        writer.writerow([expense.description, expense.amount, expense.category, expense.date])

    return response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
@login_required
def export_expenses_pdf(request):
    category = request.GET.get('category')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('q')

    expenses = Expense.objects.filter(user=request.user)

    if category and category != "All":
        expenses = expenses.filter(category=category)

    if search_query:
        expenses = expenses.filter(description__icontains=search_query)

    if sort_by == 'amount_desc':
        expenses = expenses.order_by('-amount')
    elif sort_by == 'amount_asc':
        expenses = expenses.order_by('amount')
    elif sort_by == 'date_asc':
        expenses = expenses.order_by('date')
    else:
        expenses = expenses.order_by('-date')

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=expenses.pdf'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Expense Report")

    p.setFont("Helvetica", 12)
    y = height - 80
    p.drawString(30, y, "Description")
    p.drawString(200, y, "Amount")
    p.drawString(300, y, "Category")
    p.drawString(400, y, "Date")

    y -= 20
    for exp in expenses:
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(30, y, exp.description[:30])
        p.drawString(200, y, f"₹{exp.amount}")
        p.drawString(300, y, exp.category)
        p.drawString(400, y, exp.date.strftime("%d-%m-%Y"))
        y -= 20

    p.showPage()
    p.save()
    return response

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('expense_list')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('expense_list')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
