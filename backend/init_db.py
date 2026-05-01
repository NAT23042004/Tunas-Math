"""
Database initialization script
Loads sample problems into the database
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import AsyncSessionLocal, engine
from db.models import Problem, Base, DifficultyLevel
from data.sample_problems import SAMPLE_PROBLEMS


async def init_database():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created")


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
    """Main initialization function"""
    print("Initializing Toán Socratic database...")

    try:
        await init_database()
        await load_sample_problems()
        print("\n✓ Database initialization complete!")
    except Exception as e:
        print(f"\n✗ Error during initialization: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())