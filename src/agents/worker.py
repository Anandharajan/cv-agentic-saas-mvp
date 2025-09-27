import uuid
from typing import List

try:
    import rq  # type: ignore
    import redis  # type: ignore

    RQ = True
except Exception:
    RQ = False


def enqueue_batch(payloads: List[bytes]) -> str:
    job_id = str(uuid.uuid4())
    # MVP: no real queue processing; extend to rq later
    # if RQ: enqueue to Redis queue
    return job_id
