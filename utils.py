import os
from multiprocessing import Queue
from prettytable import PrettyTable
from classes import *

def files():
    with open('data/examiners.txt', 'r', encoding='utf-8') as f:
        examiners = [Examiner(*line.strip().split()) for line in f if line.strip()]

    with open('data/students.txt', 'r', encoding='utf-8') as f:
        students = [Student(*line.strip().split()) for line in f if line.strip()]

    with open('data/questions.txt', 'r', encoding='utf-8') as f:
        questions = [Question(line.strip()) for line in f if line.strip()]

    return examiners, students, questions

def exam_process(examiner: Examiner, students_queue: Queue, results_queue: Queue, questions: List[Question]):
    start_time = time.time()

    while not students_queue.empty():
        try:
            elapsed = time.time() - start_time
            if elapsed > 30 and not examiner.on_lunch:
                print(f"{examiner.name} на обеде")
                time.sleep(random.uniform(12, 18))
                start_time = time.time()

            student = students_queue.get_nowait()
        except:
            break

        examiner.current_student = student
        results_queue.put((examiner, student, questions))

        examiner.exam_process(student, questions)

        examiner.current_student = None
        results_queue.put((examiner, student, questions))

def print_table(students, examiners, elapsed_time):
    os.system('cls' if os.name == 'nt' else 'clear')

    table_st = PrettyTable(["Студент", "Статус"])
    order = {"Очередь": 0, "Сдал": 1, "Провалил": 2}
    for s in sorted(students, key=lambda x: order[x.status]):
        table_st.add_row([s.name, s.status])
    print(table_st)

    table_ex = PrettyTable(["Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"])
    for e in examiners:
        table_ex.add_row([e.name,
                          e.current_student.name if e.current_student else "-",
                          e.students_total, e.failed_count,
                          f"{e.work_time:.2f}"])
    print(table_ex)

    queue_left = sum(1 for s in students if s.status == "Очередь")
    print(f"Осталось в очереди: {queue_left} из {len(students)}")
    print(f"Время с начала экзамена: {elapsed_time:.2f} сек.\n")


def print_result(students, examiners, questions, total_time):
    print("Итоги экзамена:\n")

    table_st = PrettyTable(["Студент", "Статус"])
    order = {"Сдал": 0, "Провалил": 1}
    for s in sorted(students, key=lambda x: order[x.status]):
        table_st.add_row([s.name, s.status])
    print(table_st)

    table_ex = PrettyTable(["Экзаменатор", "Всего студентов", "Завалил", "Время работы"])
    for e in examiners:
        table_ex.add_row([e.name, e.students_total, e.failed_count, f"{e.work_time:.2f}"])
    print(table_ex)

    print(f"\nВремя экзамена: {total_time:.2f} сек.")

    passed = [s for s in students if s.status == "Сдал"]
    if passed:
        best_st = [s.name for s in passed if s.exam_time == min(x.exam_time for x in passed)]
        print(f"Лучшие студенты: {', '.join(best_st)}")
    else:
        print("Лучших студентов нет")

    valid_ex = [e for e in examiners if e.students_total > 0]
    best_ex = [e.name for e in valid_ex if e.failed_count / e.students_total ==
               min(e.failed_count / e.students_total for e in valid_ex)]
    print(f"Лучшие экзаменаторы: {', '.join(best_ex)}")

    failed = [s for s in students if s.status == "Провалил"]
    if failed:
        expelled = [s.name for s in failed if s.exam_time == min(x.exam_time for x in failed)]
        print(f"Отчисленные студенты: {', '.join(expelled)}")

    best_q = [q.text for q in questions if q.correct_answer == max(q.correct_answer for q in questions)]
    print(f"Лучшие вопросы: {', '.join(best_q)}")

    success_rate = len(passed) / len(students)
    print("Результат:", "Экзамен удался" if success_rate > 0.85 else "Экзамен не удался")
