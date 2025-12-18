import random

# Function to generate MCQs dynamically based on topic
def get_mcq_questions(topic, num_questions=5):
    questions = []
    for i in range(num_questions):
        question_text = f"What is a key concept of {topic}?"
        options = [f"{topic} concept {j}" for j in range(1,5)]
        correct_answer = options[0]
        random.shuffle(options)  # Shuffle options so correct answer is random
        questions.append({
            "question": question_text,
            "options": options,
            "answer": correct_answer
        })
    return questions
