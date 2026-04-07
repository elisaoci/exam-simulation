import random
import time
from typing import List

class Student:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.status = "Очередь"
        self.exam_time = 0.0

class Examiner:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.students_total = 0
        self.failed_count = 0
        self.work_time = 0.0
        self.current_student = None
        self.on_lunch = False

    def mood(self, correct):
        mood = random.choices(["Bad", "Normal", "Good"], weights=[1/8, 5/8, 1/4], k=1)[0]
        if mood == "Bad":
            return False
        elif mood == "Good":
            return True
        return correct > 1

    def exam_process(self, student, questions):
        self.students_total += 1
        self.current_student = student

        exam_duration = random.uniform(len(self.name) - 1, len(self.name) + 1)
        start_time = time.time()

        correct = 0
        for q in random.sample(questions, 3):
            s_ans = q.student_answer(student.gender)
            e_ans = q.examiner_answer(self.gender)
            if s_ans in e_ans:
                correct += 1
                q.correct_answer += 1

        result = self.mood(correct)
        student.status = "Сдал" if result else "Провалил"
        if not result:
            self.failed_count += 1

        time.sleep(exam_duration)
        self.work_time += time.time() - start_time
        student.exam_time = exam_duration

        self.current_student = None

        if self.work_time > 30 and not self.on_lunch:
            self.on_lunch = True
            print(f"{self.name} ушёл на обед...")
            time.sleep(random.uniform(12, 18))

class Question:
    phi = (1 + 5 ** 0.5) / 2

    def __init__(self, text):
        self.text = text
        self.words = text.split()
        self.correct_answer = 0

    def probability_answer(self, gender):
        n = len(self.words)
        probability = []
        k = 1

        for i in range(1, n + 1):
            if i == 1:
                k = k / self.phi
                probability.append(k / self.phi)
            elif i == n:
                k -= probability[-1]
                probability.append(k)
            else:
                k -= probability[-1]
                probability.append(k / self.phi)

        if gender == 'Ж':
            probability.reverse()
        return probability

    def student_answer(self, gender):
        p = self.probability_answer(gender)
        return random.choices(self.words, weights=p, k=1)[0]

    def examiner_answer(self, gender):
        p = self.probability_answer(gender)
        remain = list(range(len(self.words)))
        result = []

        while remain:
            word_index = random.choices(remain, weights=[p[i] for i in remain], k=1)[0]
            result.append(self.words[word_index])
            remain.remove(word_index)
            if random.random() > 1 / 3:
                break
        return result
