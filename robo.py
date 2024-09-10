import random
import string
import time
from multiprocessing import Pool, cpu_count, Manager
from datetime import datetime, timedelta
import sys

def generate_passwords_for_day(args):
    current_date, min_length, max_length, include_symbols, progress = args
    chars = string.ascii_letters + string.digits  # no symbols
    passwords = []

    # simulate setting system time
    time_struct = time.strptime(current_date, '%Y-%m-%d')
    base_time = time.mktime(time_struct)

    # generate passwords every second
    for length in range(min_length, max_length + 1):
        for second in range(86400):  # 86400 seconds in a day
            # seed with the base time plus the current second
            time_seed = base_time + second
            random.seed(time_seed)
            password = ''.join(random.choice(chars) for _ in range(length))
            passwords.append(password)
            progress.put(password)

    return passwords

def display_progress(progress, total_tasks):
    total_passwords = 0
    start_time = time.time()
    while True:
        if progress.empty():
            continue
        password = progress.get()
        if password == "STOP":
            break
        total_passwords += 1
        elapsed_time = time.time() - start_time
        total_bytes = total_passwords * (len(password) + 1)  # +1 for newline character
        total_megabytes = total_bytes / (1024 * 1024)
        total_gigabytes = total_megabytes / 1024
        passwords_per_second = total_passwords / elapsed_time
        remaining_passwords = (total_tasks * (max_length - min_length + 1) * 86400) - total_passwords
        estimated_time_remaining = remaining_passwords / passwords_per_second
        sys.stdout.write(
            f"\rpasswords generated: {total_passwords:,} | size: {total_megabytes:.2f} mb / {total_gigabytes:.2f} gb | "
            f"time remaining: {estimated_time_remaining / 60:.2f} minutes"
        )
        sys.stdout.flush()

def main():
    start_date = datetime(2012, 1, 1)
    end_date = datetime(2015, 12, 31)
    min_length = 8
    max_length = 20
    include_symbols = False  # no symbols

    num_cores = min(4, cpu_count())  # limiting to 4 cores
    current_date = start_date
    dates = []

    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    total_tasks = len(dates)
    with Manager() as manager:
        progress = manager.Queue()
        tasks = [(date, min_length, max_length, include_symbols, progress) for date in dates]
        pool = Pool(num_cores)
        pool.apply_async(display_progress, (progress, total_tasks))

        all_passwords = pool.map(generate_passwords_for_day, tasks)
        progress.put("STOP")

        with open('robowordlist.txt', 'w') as f:
            for passwords in all_passwords:
                for password in passwords:
                    f.write(password + '\n')

        pool.close()
        pool.join()

    print("\npassword generation completed.")

if __name__ == "__main__":
    main()

