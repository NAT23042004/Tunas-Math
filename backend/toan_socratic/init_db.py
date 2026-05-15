"""
Database seed script
Loads sample problems into an existing schema
"""

import asyncio
from sqlalchemy import select

from toan_socratic.data.sample_problems import SAMPLE_PROBLEMS
from toan_socratic.db.database import AsyncSessionLocal
from toan_socratic.db.models import DifficultyLevel, Problem


async def load_sample_problems():
    """Load sample problems into database"""
    async with AsyncSessionLocal() as session:
        # Check if problems already exist
        result = await session.execute(select(Problem))
        existing_problems = result.scalars().all()

        if existing_problems:
            print(f"✓ Found {len(existing_problems)} existing problems")
            return

        # Load sample problems
        for problem_data in SAMPLE_PROBLEMS:
            problem = Problem(
                topic_id=problem_data["topic_id"],
                statement_latex=problem_data["statement_latex"],
                difficulty=DifficultyLevel(problem_data["difficulty"]),
                answer=problem_data["answer"],
                is_geometry=problem_data["is_geometry"],
                geometry_params=problem_data["geometry_params"],
                source=problem_data["source"],
                misconceptions=problem_data["misconceptions"]
            )
            session.add(problem)

        await session.commit()
        print(f"✓ Loaded {len(SAMPLE_PROBLEMS)} sample problems")


async def main():
    """Seed sample data after schema migrations have been applied."""
    print("Seeding Toán Socratic database...")

    try:
        await load_sample_problems()
        print("\n✓ Database seed complete!")
    except Exception as e:
        print(f"\n✗ Error during database seed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
