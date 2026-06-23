from datetime import datetime

# =========================
# MEMORY STORAGE (RUNTIME)
# =========================

USER_STATE = {}          # simpan flow user (paket, step, dll)
REF_STORAGE = {}         # simpan referral sementara
TRIAL_USED = set()       # anti double trial
PENDING_PAYMENT = {}     # simpan user yang belum di-approve


# =========================
# REFERRAL SYSTEM
# =========================

def set_ref(user_id, ref_code):
    REF_STORAGE[user_id] = ref_code


def get_ref(user_id):
    return REF_STORAGE.get(user_id)


# =========================
# USER FLOW STATE
# =========================

def set_user_state(user_id, state):
    USER_STATE[user_id] = state


def get_user_state(user_id):
    return USER_STATE.get(user_id)


def clear_user_state(user_id):
    if user_id in USER_STATE:
        del USER_STATE[user_id]


# =========================
# TRIAL CONTROL
# =========================

def has_used_trial(user_id):
    return user_id in TRIAL_USED


def mark_trial_used(user_id):
    TRIAL_USED.add(user_id)


# =========================
# PAYMENT FLOW
# =========================

def set_pending_payment(user_id, data):
    """
    data contoh:
    {
        package: "1bulan",
        username: "...",
        ref: "FACHRI"
    }
    """
    PENDING_PAYMENT[user_id] = {
        **data,
        "time": datetime.now()
    }


def get_pending_payment(user_id):
    return PENDING_PAYMENT.get(user_id)


def clear_pending_payment(user_id):
    if user_id in PENDING_PAYMENT:
        del PENDING_PAYMENT[user_id]
