"""Team collaboration endpoints."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.team import (
    TeamCreate,
    TeamResponse,
    InviteTeamMemberRequest,
    TeamInvitationResponse,
    AcceptInvitationRequest,
    TeamMemberResponse,
)
from app.services.team_service import TeamService

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=TeamResponse, status_code=201)
@limiter.limit("10/minute")
async def create_team(
    request: Request,
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new team."""
    service = TeamService(db)
    team = await service.create_team(
        owner_id=current_user.id,
        name=team_data.name,
        description=team_data.description,
    )
    return team


@router.get("", response_model=List[TeamResponse])
@limiter.limit("60/minute")
async def list_teams(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's teams."""
    service = TeamService(db)
    teams = await service.list_teams(current_user.id)
    return teams


@router.post("/{team_id}/invite", response_model=TeamInvitationResponse)
@limiter.limit("20/minute")
async def invite_member(
    request: Request,
    team_id: UUID,
    invite_data: InviteTeamMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Invite member to team."""
    service = TeamService(db)
    invitation = await service.invite_member(
        team_id=team_id,
        email=invite_data.email,
        role=invite_data.role,
        invited_by=current_user.id,
    )
    return invitation


@router.post("/accept-invitation", response_model=TeamMemberResponse)
@limiter.limit("20/minute")
async def accept_invitation(
    request: Request,
    accept_data: AcceptInvitationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept team invitation."""
    service = TeamService(db)
    try:
        member = await service.accept_invitation(
            token=accept_data.token,
            user_id=current_user.id,
        )
        return member
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
@limiter.limit("60/minute")
async def get_team_members(
    request: Request,
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get team members."""
    service = TeamService(db)
    members = await service.get_team_members(team_id)
    return members


@router.delete("/{team_id}/members/{user_id}", status_code=204)
@limiter.limit("20/minute")
async def remove_member(
    request: Request,
    team_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove team member."""
    service = TeamService(db)
    success = await service.remove_member(team_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found or cannot remove owner")
