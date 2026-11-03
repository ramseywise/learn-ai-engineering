from lease_scheduler import LeaseScheduler


def test_double_fire_makes_one_run():
    s = LeaseScheduler()
    s.add("job", 100)
    s.add("job", 100)
    assert s.claim("a", 100) == ("job", 100, 1)
    assert s.claim("b", 100) is None


def test_not_due_yet():
    s = LeaseScheduler()
    s.add("job", 100)
    assert s.claim("a", 99.9) is None


def test_oldest_first():
    s = LeaseScheduler()
    s.add("late", 200)
    s.add("early", 100)
    assert s.claim("a", 300)[0] == "early"


def test_stale_worker_cannot_finish():
    s = LeaseScheduler()
    s.add("job", 100)
    first = s.claim("a", 100, lease=30)
    second = s.claim("b", 130, lease=30)
    assert second[2] == first[2] + 1
    assert not s.finish(*first, "from a")
    assert s.finish(*second, "from b")
    assert s.effects() == [("job", 2, "from b")]
    assert s.state("job", 100) == "done"


def test_heartbeat_renews_the_lease():
    s = LeaseScheduler()
    s.add("job", 100)
    job = s.claim("a", 100, lease=30)
    assert s.heartbeat(*job, now=120, lease=30)
    assert s.claim("b", 149) is None      # would have expired at 130 without the heartbeat
    assert s.claim("b", 150) is not None


def test_stale_heartbeat_tells_the_worker_to_stop():
    s = LeaseScheduler()
    s.add("job", 100)
    first = s.claim("a", 100, lease=30)
    s.claim("b", 131, lease=30)
    assert not s.heartbeat(*first, now=132)


def test_finished_run_is_not_handed_out_or_finished_again():
    s = LeaseScheduler()
    s.add("job", 100)
    job = s.claim("a", 100, lease=30)
    assert s.finish(*job, "x")
    assert s.claim("b", 1000) is None
    assert not s.finish(*job, "again")


def test_poison_job_stops_after_max_attempts():
    s = LeaseScheduler()
    s.add("poison", 100)
    s.add("good", 101)
    now = 100
    for attempt in (1, 2, 3):
        assert s.claim("a", now, lease=10, max_attempts=3) == ("poison", 100, attempt)
        now += 10
    assert s.claim("a", now, lease=10, max_attempts=3)[0] == "good"
    assert s.state("poison", 100) == "failed"
