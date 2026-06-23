users_ref = {}
pending_payment = {}
trial_used = set()


def set_ref(user_id, ref):
    users_ref[user_id] = ref


def get_ref(user_id):
    return users_ref.get(user_id, "")


def set_pending_payment(user_id, data):
    pending_payment[user_id] = data


def get_pending_payment(user_id):
    return pending_payment.get(user_id)


def clear_pending_payment(user_id):
    pending_payment.pop(user_id, None)


def mark_trial_used(user_id):
    trial_used.add(user_id)


def has_used_trial(user_id):
    return user_id in trial_used
