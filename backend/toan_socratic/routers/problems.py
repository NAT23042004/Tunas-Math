from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from toan_socratic.db.database import get_db
from toan_socratic.db.models import DifficultyLevel, Problem
from toan_socratic.db.schemas import ProblemCreate, ProblemResponse


router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=List[ProblemResponse])
async def get_problems(
    topic_id: Optional[str] = Query(None, description="Filter by topic"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    is_geometry: Optional[bool] = Query(None, description="Filter geometry problems"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: AsyncSession = Depends(get_db)
):
    """Get problems with optional filters"""
    query = select(Problem)

    # Apply filters
    if topic_id:
        query = query.where(Problem.topic_id == topic_id)
    if difficulty:
        query = query.where(Problem.difficulty == difficulty)
    if is_geometry is not None:
        query = query.where(Problem.is_geometry == is_geometry)

    # Apply limit and order
    query = query.order_by(Problem.created_at.desc()).limit(limit)

    result = await db.execute(query)
    problems = result.scalars().all()

    return problems


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get problem by ID"""
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )

    return problem


@router.get("/{problem_id}/geometry")
async def get_problem_geometry(
    problem_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get geometry parameters for a problem"""
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )

    if not problem.is_geometry or not problem.geometry_params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Problem is not a geometry problem"
        )

    return {
        "solid_type": problem.geometry_params.get("solid_type"),
        "params": problem.geometry_params.get("params"),
        "labels": problem.geometry_params.get("labels")
    }


@router.post("", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new problem"""
    new_problem = Problem(
        topic_id=problem_data.topic_id,
        statement_latex=problem_data.statement_latex,
        difficulty=problem_data.difficulty,
        answer=problem_data.answer,
        is_geometry=problem_data.is_geometry,
        geometry_params=problem_data.geometry_params,
        source=problem_data.source,
        misconceptions=problem_data.misconceptions
    )

    db.add(new_problem)
    await db.commit()
    await db.refresh(new_problem)

    return new_problem
