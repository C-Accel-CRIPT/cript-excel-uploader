def standardize_name(name):
    return name.replace(" ", "").lower()


def process_track(msg, count, total_count):
    count = count + 1
    if count != 0 and count % 10 == 0:
        print(f"{msg}: {count}/{total_count}")
