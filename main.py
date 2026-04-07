from utils import *
from multiprocessing import Process

def main():
    examiners, students, questions = files()

    students_queue = Queue()
    for s in students:
        students_queue.put(s)

    results_queue = Queue()

    processes = []
    for e in examiners:
        p = Process(target=exam_process, args=(e, students_queue, results_queue, questions))
        p.start()
        processes.append(p)

    start_time = time.time()

    while any(p.is_alive() for p in processes) or not results_queue.empty():
        while not results_queue.empty():
            ex, st, qlist = results_queue.get()

            for i, s in enumerate(students):
                if s.name == st.name:
                    students[i] = st

            for i, e in enumerate(examiners):
                if e.name == ex.name:
                    examiners[i] = ex

            questions = qlist

        print_table(students, examiners, time.time() - start_time)
        time.sleep(0.5)

    for p in processes:
        p.join()

    print_result(students, examiners, questions, time.time() - start_time)


if __name__ == "__main__":
    main()
