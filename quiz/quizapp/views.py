from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
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

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
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

# ---------------- MCQ GENERATOR ----------------
def generate_mcqs(topic, difficulty):
    questions = [
        {
            "question": f"What is {topic}?",
            "options": [
                f"{topic} is a programming language",
                f"{topic} is a hardware device",
                f"{topic} is a sport",
                f"{topic} is a database"
            ],
            "answer": "A"
        },
        {
            "question": f"Which field uses {topic} the most?",
            "options": [
                "Education",
                "Healthcare",
                "Technology",
                "All of the above"
            ],
            "answer": "D"
        },
        {
            "question": f"Is {topic} useful for beginners?",
            "options": [
                "Yes",
                "No",
                "Only experts",
                "Not related"
            ],
            "answer": "A"
        }
    ]

    if difficulty == "easy":
        return questions[:2]
    return questions

# ---------------- DASHBOARD ----------------
@login_required(login_url="signin")
def dashboard(request):
    if request.method == "POST":
        topic = request.POST.get("topic", "General")
        difficulty = request.POST.get("difficulty", "easy")

        questions = generate_mcqs(topic, difficulty)

        request.session['questions'] = questions
        request.session['current_question'] = 0
        request.session['score'] = 0
        request.session['topic'] = topic
        request.session['difficulty'] = difficulty

        return redirect("quiz")

    return render(request, "dashboard.html")

# ---------------- QUIZ ----------------
@login_required(login_url="signin")
def quiz(request):
    questions = request.session.get('questions', [])
    current_index = request.session.get('current_question', 0)
    score = request.session.get('score', 0)

    # Quiz finished
    if current_index >= len(questions):
        # Save score in DB
        QuizScore.objects.create(
            user=request.user,
            topic=request.session.get('topic', 'Unknown'),
            score=score
        )

        # Clear session
        request.session.flush()

        return render(request, "quiz_result.html", {
            "score": score,
            "total": len(questions)
        })

    if request.method == "POST":
        selected = request.POST.get("option")  # Must match the <input name="option">
        correct = questions[current_index]["answer"]  # Current question's answer

        if selected == correct:
            score += 1
            request.session['score'] = score

        # Move to next question
        request.session['current_question'] = current_index + 1

        return redirect('quiz')  # Redirect to refresh page with next question

    # Show current question
    question = questions[current_index]

    return render(request, "quiz_page.html", {
        "question": question,
        "current": current_index + 1,
        "total": len(questions)
    })

# @login_required(login_url="signin")
# def quiz(request):
#     questions = request.session.get('questions', [])
#     current_index = request.session.get('current_question', 0)
#     score = request.session.get('score', 0)

#     # Quiz finished
#     if current_index >= len(questions):
#         QuizScore.objects.create(
#             user=request.user,
#             topic=request.session.get('topic', 'Unknown'),
#             score=score
#         )

#         context = {
#             "score": score,
#             "total": len(questions)
#         }

#         request.session.flush()
#         return render(request, "quiz_result.html", context)

#     if request.method == "POST":
#         selected = request.POST.get("option")
#         correct = questions[current_index - 1]["answer"]

#         if selected == correct:
#             request.session['score'] = score + 1

#     question = questions[current_index]
#     request.session['current_question'] = current_index + 1

#     return render(request, "quiz_page.html", {
#         "question": question,
#         "current": current_index + 1,
#         "total": len(questions)
#     })

# ---------------- HISTORY ----------------
@login_required(login_url="signin")
def history(request):
    results = QuizScore.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "history.html", {
        "results": results
    })

# ---------------- LEADERBOARD ----------------
@login_required(login_url="signin")
def leaderboard(request):
    leaders = (
        QuizScore.objects
        .values("user__username")
        .annotate(total_score=Sum("score"))
        .order_by("-total_score")[:10]
    )

    return render(request, "leaderboard.html", {
        "leaders": leaders
    })
