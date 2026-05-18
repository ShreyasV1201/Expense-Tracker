import calendar
import io
import json
from datetime import date, datetime, timedelta
from urllib.request import urlopen
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import openpyxl
import requests
from openpyxl import Workbook
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .forms import ExpenseForm, IncomeForm, ProfileForm, RecurringExpenseForm
from .models import Expense, Income, Profile, Recurring_expenses



User = get_user_model() 



def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

class MyLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_valid(self, form):
        remember = self.request.POST.get('remember') == 'on'
        if not remember:
            # expire the session on browser close
            self.request.session.set_expiry(0)
        return super().form_valid(form)

class MyLogoutView(LogoutView):
    # uses LOGOUT_REDIRECT_URL from settings
    pass
@login_required
def home(request):
    today = date.today()
    month_start = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    month_end = today.replace(day=last_day)

    income_qs = Income.objects.filter(
        user=request.user,
        date__gte=month_start,
        date__lte=month_end
    )
    expense_qs = Expense.objects.filter(
        user=request.user,
        date__gte=month_start,
        date__lte=month_end
    )

    total_income = income_qs.aggregate(sum=Sum('amount'))['sum'] or 0
    total_expenses = expense_qs.aggregate(sum=Sum('amount'))['sum'] or 0
    net_income = total_income - total_expenses

    context = {
        'month_name': today.strftime("%B"),
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_income': net_income,
    }
    return render(request, 'dashboard.html', context)
@login_required
def add_expense(request):
    # Handle the POST form for creating a new expense
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            return redirect('add_expense')
    else:
        form = ExpenseForm()

    # ---- new filter code starts here ----
    qs = Expense.objects.filter(user=request.user)
    start = request.GET.get('start_date')
    end   = request.GET.get('end_date')
    if start and end:
        try:
            sd = datetime.strptime(start, "%Y-%m-%d").date()
            ed = datetime.strptime(end,   "%Y-%m-%d").date()
            qs = qs.filter(date__range=(sd, ed))
        except ValueError:
            pass
    # ---- filter code ends here ----

    # Order & send to template
    expenses = qs.order_by('-date')
    return render(request, 'AddExpense.html', {
        'form':     form,
        'expenses': expenses,
    })

class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        fields = ['date', 'category', 'amount', 'description']

@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
        return redirect('add_expense')   # always bounce back to the modal page

    # if someone somehow navigates here via GET, just redirect
    return redirect('add_expense')

@login_required
@require_POST
def delete_expense(request, pk):
    """
    Deletes an expense and redirects back to the list.
    Only accepts POST to prevent CSRF holes.
    """
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('add_expense')

@login_required
def income_tracker(request):
    # you can load data here, e.g. incomes = Income.objects.filter(user=request.user)
    return render(request, 'incomeTracker.html', {})

@login_required
def income_tracker(request):
    # ——— 1) Handle creation of a new income entry ———
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            inc = form.save(commit=False)
            inc.user = request.user
            inc.save()
            return redirect('income_tracker')
    else:
        form = IncomeForm()

    # ——— 2) Build & Filter the queryset on GET params ———
    qs = Income.objects.filter(user=request.user)
    start = request.GET.get('start_date')
    end   = request.GET.get('end_date')
    if start and end:
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d").date()
            end_dt   = datetime.strptime(end,   "%Y-%m-%d").date()
            qs = qs.filter(date__range=(start_dt, end_dt))
        except ValueError:
            # invalid date format; you could add a message here
            pass

    # ——— 3) Order and render ———
    incomes = qs.order_by('-date')
    return render(request, 'incomeTracker.html', {
        'form':    form,
        'incomes': incomes,
    })
@login_required
def income_tracker(request):
    # ——— 1) CREATE on POST ———
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            inc = form.save(commit=False)
            inc.user = request.user
            inc.save()
            return redirect('income_tracker')
    else:
        form = IncomeForm()

    # ——— 2) FILTER on GET ———
    qs = Income.objects.filter(user=request.user)
    start = request.GET.get('start_date')
    end   = request.GET.get('end_date')
    if start and end:
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d").date()
            end_dt   = datetime.strptime(end,   "%Y-%m-%d").date()
            qs = qs.filter(date__range=(start_dt, end_dt))
        except ValueError:
            pass

    incomes = qs.order_by('-date')
    return render(request, 'incomeTracker.html', {
        'form':    form,
        'incomes': incomes,
    })

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('income_tracker')
    else:
        form = IncomeForm()

    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'incomeTracker.html', {
        'form':    form,
        'incomes': incomes,
    })


@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
        return redirect('income_tracker')
    return redirect('income_tracker')


@login_required
@require_POST
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    income.delete()
    return redirect('income_tracker')


@login_required
def profile(request):
    # 1) Get or create the Profile for this user
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # 2) Bind POST data to the form AND the existing instance
        form = ProfileForm(request.POST, instance=profile_obj)

        if form.is_valid():
            # 3) Save, ensuring the FK is set on first save
            updated_profile = form.save(commit=False)
            updated_profile.user = request.user
            updated_profile.save()
            messages.success(request, "Your profile was updated!")
            return redirect('profile')    # Prevent re-POST on reload
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        # 4) On GET, prefill the form from the instance
        form = ProfileForm(instance=profile_obj)

    return render(request, 'profile.html', {
        'profile': profile_obj,
        'form':    form,
    })
  
def expense_list(request):
    qs = Expense.objects.filter(user=request.user)

    # pull from GET
    start = request.GET.get('start_date')
    end   = request.GET.get('end_date')

    if start and end:
        try:
            # parse yyyy-mm-dd dates
            start_dt = datetime.strptime(start, "%Y-%m-%d").date()
            end_dt   = datetime.strptime(end,   "%Y-%m-%d").date()
            qs = qs.filter(date__range=(start_dt, end_dt))
        except ValueError:
            # ignore invalid dates (or add an error message)
            pass

    # then paginate / context as usual
    context = {
        'expenses': qs.order_by('-date'),
        # … any pagination data …
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def recurring_expenses(request):
    # handle form POST
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            # after saving, redirect to clear POST data
            return redirect('recurring_expenses')
    else:
        form = RecurringExpenseForm()

    # always fetch the list
    expenses = Recurring_expenses.objects.filter(user=request.user)
    return render(request, 'recurring_expenses.html', {
        'expenses': expenses,
        'form': form,
    })  

@login_required
def edit_recurring_expense(request, pk):
    expense = get_object_or_404(Recurring_expenses, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('recurring_expenses')
    else:
        form = RecurringExpenseForm(instance=expense)

    return render(request, 'expenses/edit_recurring_expense.html', {
        'form': form,
        'expense': expense,
    })

@require_POST
@login_required
def delete_recurring_expense(request, pk):
    """
    Delete a single Recurring_expenses instance if it belongs to the current user.
    """
    expense = get_object_or_404(Recurring_expenses, pk=pk, user=request.user)
    expense.delete()
    return redirect('recurring_expenses')

@login_required
def export_expenses(request):
    # 1) Parse your existing date filters (adjust param names to match your template)
    start = request.GET.get('from')  # expects   yyyy-mm-dd or whatever format you use
    end   = request.GET.get('to')

    qs = Expense.objects.filter(user=request.user)
    if start:
        qs = qs.filter(date__gte=datetime.fromisoformat(start))
    if end:
        qs = qs.filter(date__lte=datetime.fromisoformat(end))

    # 2) Create workbook & sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Expenses"

    # 3) Write headers
    ws.append(["Date", "Category", "Description", "Amount"])

    # 4) Write each row
    for e in qs.order_by("date"):
        ws.append([
            e.date.strftime("%Y-%m-%d"),
            e.category,
            e.description,
            float(e.amount),
        ])

    # 5) Build response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename=expenses.xlsx'
    wb.save(response)
    return response

def export_incomes(request):
    """
    Export Income records to an Excel file, filtered by start_date / end_date.
    """
    # Grab GET params
    start_date = request.GET.get('start_date')
    end_date   = request.GET.get('end_date')

    # Build queryset
    qs = Income.objects.all().order_by('date')
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)

    # Create workbook & sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Incomes"

    # Header row
    ws.append(['Date', 'Category', 'Description', 'Amount (₹)'])

    # Data rows
    for inc in qs:
        ws.append([
            inc.date.strftime('%Y-%m-%d'),
            inc.category,
            inc.description or '',
            float(inc.amount),
        ])

    # Prepare HTTP response
    filename = f"incomes_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'
        )
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Save workbook into response
    wb.save(response)
    return response


CURRENCY_NAMES = {
    "USD": "US Dollar",
    "INR": "Indian Rupee",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",
    # …add more if you like, or omit and rely on API list…
}

from datetime import date, timedelta
import calendar
from django.db.models import Sum, Q
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Income, Expense, Recurring_expenses  # make sure this import is correct

@csrf_protect
@login_required
@csrf_protect
@login_required
def dashboard(request):
    # 1) Bounds of “this month”
    today       = date.today()
    month_start = today.replace(day=1)
    last_day    = calendar.monthrange(today.year, today.month)[1]
    month_end   = today.replace(day=last_day)

    # 2) One‐time Income/Expense this month
    income_qs  = Income.objects.filter(
        user=request.user,
        date__gte=month_start, date__lte=month_end
    )
    expense_qs = Expense.objects.filter(
        user=request.user,
        date__gte=month_start, date__lte=month_end
    )
    total_income   = income_qs.aggregate(sum=Sum('amount'))['sum'] or 0
    total_expenses = expense_qs.aggregate(sum=Sum('amount'))['sum'] or 0

    # 3) This month’s Recurring‐expense total (projected)
    active_recurs = Recurring_expenses.objects.filter(
        user=request.user,
        status='active',
        start_date__lte=month_end
    ).filter(
        Q(end_date__gte=month_start) | Q(end_date__isnull=True)
    )
    recurring_total = 0
    for exp in active_recurs:
        w0 = max(exp.start_date, month_start)
        w1 = min(exp.end_date, month_end) if exp.end_date else month_end
        if w0 > w1:
            continue

        if exp.frequency == 'daily':
            occ = (w1 - w0).days + 1
        elif exp.frequency == 'weekly':
            sd_wd = exp.start_date.weekday()
            w0_wd = w0.weekday()
            shift = (sd_wd - w0_wd) % 7
            fo    = w0 + timedelta(days=shift)
            occ   = 0 if fo > w1 else ((w1 - fo).days // 7) + 1
        elif exp.frequency == 'monthly':
            occ = 1
        elif exp.frequency == 'yearly':
            occ = 1 if exp.start_date.month == month_start.month else 0
        else:
            occ = 0

        recurring_total += exp.amount * occ

    # 4) Net income after recurring
    net_income = total_income - total_expenses - recurring_total

    # ——————————————————————————————————————————
    # BAR-CHART DATA PREP (12 months)
    # ——————————————————————————————————————————
    base_recurs = Recurring_expenses.objects.filter(
        user=request.user, status='active'
    )

    months            = []
    monthly_income    = []
    monthly_expenses  = []
    monthly_recurring = []

    for m in range(1, 13):
        m_start = date(today.year, m, 1)
        m_end   = date(today.year, m, calendar.monthrange(today.year, m)[1])

        months.append(m_start.strftime('%b'))

        inc_val = Income.objects.filter(
            user=request.user, date__gte=m_start, date__lte=m_end
        ).aggregate(sum=Sum('amount'))['sum'] or 0
        exp_val = Expense.objects.filter(
            user=request.user, date__gte=m_start, date__lte=m_end
        ).aggregate(sum=Sum('amount'))['sum'] or 0

        monthly_income.append(float(inc_val))
        monthly_expenses.append(float(exp_val))

        rec_m = 0
        for exp_r in base_recurs:
            w0 = max(exp_r.start_date, m_start)
            w1 = min(exp_r.end_date, m_end) if exp_r.end_date else m_end
            if w0 > w1:
                continue

            if exp_r.frequency == 'daily':
                occ = (w1 - w0).days + 1
            elif exp_r.frequency == 'weekly':
                sd_wd = exp_r.start_date.weekday()
                w0_wd = w0.weekday()
                shift = (sd_wd - w0_wd) % 7
                fo    = w0 + timedelta(days=shift)
                occ   = 0 if fo > w1 else ((w1 - fo).days // 7) + 1
            elif exp_r.frequency == 'monthly':
                occ = 1
            elif exp_r.frequency == 'yearly':
                occ = 1 if exp_r.start_date.month == m else 0
            else:
                occ = 0

            rec_m += exp_r.amount * occ

        monthly_recurring.append(float(rec_m))

    # 5) Currency‐converter inputs & rates
    from_curr  = request.POST.get("from_currency", "USD")
    to_curr    = request.POST.get("to_currency",   "INR")
    amount_str = request.POST.get("amount", "")

    try:
        url   = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
        with urlopen(url) as resp:
            data = json.load(resp)
        codes = sorted(data["rates"].keys())
    except Exception:
        data  = {"rates": {}}
        codes = sorted(CURRENCY_NAMES.keys())

    choices = [(code, CURRENCY_NAMES.get(code, code)) for code in codes]

    converted_amount = None
    if request.method == "POST" and amount_str:
        try:
            amt  = float(amount_str)
            rate = data["rates"].get(to_curr)
            if rate is not None:
                converted_amount = round(amt * rate, 2)
        except ValueError:
            pass

    # 6) Render all context
    return render(request, "dashboard.html", {
        "month_name"       : today.strftime("%B"),
        "total_income"     : total_income,
        "total_expenses"   : total_expenses,
        "recurring_total"  : recurring_total,
        "net_income"       : net_income,
        # Chart.js data:
        "months"           : json.dumps(months),
        "monthly_income"   : json.dumps(monthly_income),
        "monthly_expenses" : json.dumps(monthly_expenses),
        "monthly_recurring": json.dumps(monthly_recurring),
        # Currency converter:
        "choices"          : choices,
        "from_currency"    : from_curr,
        "to_currency"      : to_curr,
        "amount"           : amount_str,
        "converted_amount" : converted_amount,
    })


@login_required
def expense_pie_chart(request):
    # 1) Aggregate total per category
    data = (
        Expense.objects
        .filter(user=request.user)
        .values('category')
        .annotate(total=Sum('amount'))
    )

    labels = [d['category'] for d in data]
    sizes  = [float(d['total']) for d in data]

    # 1.5) Compute normalized percentages and explode for small slices
    total = sum(sizes)
    sizes_normed = [s / total * 100 for s in sizes]
    explode = [
        0.1 if pct < 5 else 0.0
        for pct in sizes_normed
    ]

    # 2) Define a lighter, translucent color palette (RGBA with alpha=0.6)
    colors = [
    (52/255, 152/255, 219/255, 0.8),  # brighter blue (rgba(52,152,219,0.8))
    (231/255, 76/255,  60/255,  0.8),  # vivid red   (rgba(231,76,60,0.8))
    (46/255,  204/255, 113/255, 0.8),  # vivid green (rgba(46,204,113,0.8))
    (241/255, 196/255, 15/255,  0.8),  # vivid yellow(rgba(241,196,15,0.8))
    (155/255, 89/255,  182/255, 0.8),  # brighter purple(rgba(155,89,182,0.8))
    (243/255, 156/255, 18/255,  0.8),  # brighter orange(rgba(243,156,18,0.8))
]
    # 3) Build the pie chart with transparent colors
    fig, ax = plt.subplots()
    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        explode=explode,
        pctdistance=0.7,
        labeldistance=1.1,
        textprops={'fontsize': 8},
        colors=colors
    )
    ax.axis('equal')

    # 4) Render to PNG in memory
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    # 5) Return image response
    return HttpResponse(buf.getvalue(), content_type='image/png')


@login_required
def income_expense_bar_chart(request):
    # figure out “this month”
    today       = date.today()
    month_start = today.replace(day=1)
    last_day    = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    # aggregate totals
    inc_total = (
        Income.objects
        .filter(user=request.user, date__range=(month_start, last_day))
        .aggregate(sum=Sum('amount'))['sum'] or 0
    )
    exp_total = (
        Expense.objects
        .filter(user=request.user, date__range=(month_start, last_day))
        .aggregate(sum=Sum('amount'))['sum'] or 0
    )

    # make bar chart
    labels = ['Income', 'Expenses']
    values = [float(inc_total), float(exp_total)]

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=['#2DCE89', '#dc3545'])
    ax.set_ylabel('Amount (₹)')
    ax.set_title(f'{today.strftime("%B")} Income vs Expenses')
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # render to PNG
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')
    