from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .ai import get_mcq_questions
from .models import QuizScore

# ---------------- HOME ----------------
def home(request):
    return render(request, "home.html")

# ---------------- SIGNUP ----------------
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully")
        return redirect("signin")

    return render(request, "signup.html")

# ---------------- SIGNIN ----------------
def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")
            return redirect("signin")

    return render(request, "signin.html")

# ---------------- LOGOUT ----------------
@login_required(login_url="signin")
def signout(request):
    logout(request)
    return redirect("signin")

# ---------------- DASHBOARD ----------------
@login_required(login_url="signin")
def dashboard(request):
    if request.method == "POST":
        topic = request.POST.get("topic", "General")
        difficulty = request.POST.get("difficulty", "easy")
        questions = get_mcq_questions(topic, num_questions=5)

        # Save questions and metadata in session
        request.session['questions'] = questions
        request.session['current_question'] = 0
        request.session['score'] = 0
        request.session['topic'] = topic
        request.session['difficulty'] = difficulty

        return redirect('quiz')

    return render(request, 'dashboard.html')

# ---------------- QUIZ PAGE ----------------
@login_required(login_url="signin")
def quiz(request):
    questions = request.session.get('questions', [])
    current_index = request.session.get('current_question', 0)
    score = request.session.get('score', 0)

    if request.method == "POST":
        selected_answer = request.POST.get('option')
        if selected_answer:
            correct_answer = questions[current_index - 1]['answer']
            if selected_answer == correct_answer:
                score += 1
                request.session['score'] = score

    # Quiz finished
    if current_index >= len(questions):
        # Save score in database
        QuizScore.objects.create(
            user=request.user,
            topic=request.session.get('topic', 'Unknown'),
            score=score
        )

        context = {
            "score": score,
            "total": len(questions)
        }

        # Clear session data
        request.session.pop('questions')
        request.session.pop('current_question')
        request.session.pop('score')
        request.session.pop('topic')
        request.session.pop('difficulty', None)

        return render(request, 'quiz_result.html', context)

    # Show next question
    question = questions[current_index]
    request.session['current_question'] = current_index + 1

    context = {
        "question": question,
        "current": current_index + 1,
        "total": len(questions)
    }

    return render(request, 'quiz_page.html', context)


from django.contrib.auth.decorators import login_required
from .models import QuizScore

# ---------------- HISTORY ----------------
@login_required(login_url="signin")
def history(request):
    # Fetch all quiz scores of the logged-in user, latest first
    results = QuizScore.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "history.html", {"results": results})


from django.contrib.auth.decorators import login_required
from .models import QuizScore
from django.db.models import Sum

# ---------------- LEADERBOARD ----------------
@login_required(login_url="signin")
def leaderboard(request):
    # Aggregate total score per user
    leaderboard_data = (
        QuizScore.objects.values('user__username')
        .annotate(total_score=Sum('score'))
        .order_by('-total_score')[:10]  # Top 10
    )
    return render(request, "leaderboard.html", {"leaders": leaderboard_data})


def about(request):
    return render(request, "about.html")
