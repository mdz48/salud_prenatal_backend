import asyncio
from unittest.mock import MagicMock, patch

import main as main_module


def _run_lifespan_with_fake_scheduler():
    fake_scheduler = MagicMock()

    async def _run():
        with patch("main.AsyncIOScheduler", return_value=fake_scheduler):
            async with main_module.lifespan(main_module.app):
                pass

    asyncio.run(_run())
    return fake_scheduler


class TestSchedulerWiring:
    def test_registers_daily_bitacora_reminder_at_9am_cron(self):
        fake_scheduler = _run_lifespan_with_fake_scheduler()

        daily_call = next(
            c for c in fake_scheduler.add_job.call_args_list
            if c.args[0] is main_module.send_daily_bitacora_reminder_job
        )
        assert daily_call.args[1] == "cron"
        assert daily_call.kwargs == {"hour": 9, "minute": 0}

    def test_still_registers_appointment_reminder_interval_job(self):
        # No debe romper el job de citas preexistente.
        fake_scheduler = _run_lifespan_with_fake_scheduler()

        appointment_call = next(
            c for c in fake_scheduler.add_job.call_args_list
            if c.args[0] is main_module.notify_upcoming_appointments_job
        )
        assert appointment_call.args[1] == "interval"
        assert appointment_call.kwargs == {"minutes": 15}

    def test_starts_and_shuts_down_scheduler(self):
        fake_scheduler = _run_lifespan_with_fake_scheduler()

        fake_scheduler.start.assert_called_once()
        fake_scheduler.shutdown.assert_called_once()

    def test_registers_exactly_two_jobs(self):
        fake_scheduler = _run_lifespan_with_fake_scheduler()
        assert fake_scheduler.add_job.call_count == 2
