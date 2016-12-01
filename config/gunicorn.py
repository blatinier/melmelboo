import multiprocessing

bind = "127.0.0.1:8004"
workers = multiprocessing.cpu_count() * 1 + 1
