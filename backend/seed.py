"""Seed the database with demo data."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, init_db
from models import User, Task, TaskStatus
from services.auth import hash_password


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded, skipping.")
            return

        # Create admin user
        admin = User(
            email="admin@sprintsync.dev",
            username="admin",
            hashed_password=hash_password("admin123"),
            is_admin=True,
        )

        # Create regular engineers
        alice = User(
            email="alice@sprintsync.dev",
            username="alice",
            hashed_password=hash_password("alice123"),
        )
        bob = User(
            email="bob@sprintsync.dev",
            username="bob",
            hashed_password=hash_password("bob123"),
        )

        db.add_all([admin, alice, bob])
        db.flush()

        # Create sample tasks
        tasks = [
            Task(title="Set up CI pipeline", description="Configure GitHub Actions for lint, test, and Docker build on every push.", status=TaskStatus.done, total_minutes=90, owner_id=alice.id),
            Task(title="Design auth system", description="Implement JWT-based authentication with refresh token support.", status=TaskStatus.done, total_minutes=120, owner_id=alice.id),
            Task(title="Build task CRUD API", description="FastAPI endpoints for full task lifecycle management.", status=TaskStatus.in_progress, total_minutes=60, owner_id=alice.id),
            Task(title="Add AI suggest endpoint", description="Integrate OpenAI API to generate task descriptions and daily plans.", status=TaskStatus.review, total_minutes=45, owner_id=alice.id),
            Task(title="Write integration tests", description="Cover /ai/suggest stub and core CRUD flows with pytest.", status=TaskStatus.backlog, total_minutes=0, owner_id=alice.id),

            Task(title="Database schema design", description="Define relational schema for users and tasks with migrations.", status=TaskStatus.done, total_minutes=45, owner_id=bob.id),
            Task(title="Frontend SPA scaffold", description="React app with task list, auth, and API integration.", status=TaskStatus.in_progress, total_minutes=75, owner_id=bob.id),
            Task(title="Observability middleware", description="Add structured JSON logging and Prometheus-style metrics.", status=TaskStatus.backlog, total_minutes=0, owner_id=bob.id),
            Task(title="Docker + compose setup", description="Containerize app and DB, ensure dev parity with production.", status=TaskStatus.backlog, total_minutes=0, owner_id=bob.id),
            Task(title="Deploy to Render", description="Deploy containerized app to free-tier Render cloud service.", status=TaskStatus.backlog, total_minutes=0, owner_id=bob.id),
        ]

        db.add_all(tasks)
        db.commit()
        print("✅ Database seeded successfully!")
        print("  Admin:  admin / admin123")
        print("  Alice:  alice / alice123")
        print("  Bob:    bob   / bob123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
