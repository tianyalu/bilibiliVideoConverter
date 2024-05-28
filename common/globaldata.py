succeed_count = 0
total_count = 0


def add_succeed_count(count):
    global succeed_count
    succeed_count = succeed_count + count


def reduce_succeed_count(count):
    global succeed_count
    succeed_count = succeed_count + count


def reset_succeed_count():
    global succeed_count
    succeed_count = 0


def get_succeed_count():
    return succeed_count


def add_total_count(count):
    global total_count
    total_count = total_count + count


def reduce_total_count(count):
    global total_count
    total_count = total_count + count


def reset_total_count():
    global total_count
    total_count = 0


def get_total_count():
    return total_count

