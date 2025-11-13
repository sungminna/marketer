"""Team collaboration service."""
import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.team import Team, TeamMember, TeamInvitation
from app.models.user import User


class TeamService:
    """Service for team collaboration."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_team(
        self,
        owner_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
    ) -> Team:
        """Create a new team."""
        team = Team(
            id=uuid.uuid4(),
            owner_id=owner_id,
            name=name,
            description=description,
        )

        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)

        # Add owner as team member
        member = TeamMember(
            team_id=team.id,
            user_id=owner_id,
            role="owner",
        )
        self.db.add(member)
        await self.db.commit()

        return team

    async def invite_member(
        self,
        team_id: uuid.UUID,
        email: str,
        role: str,
        invited_by: uuid.UUID,
    ) -> TeamInvitation:
        """Invite a new team member."""
        invitation = TeamInvitation(
            team_id=team_id,
            email=email,
            role=role,
            invited_by=invited_by,
        )

        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)

        return invitation

    async def accept_invitation(
        self,
        token: str,
        user_id: uuid.UUID,
    ) -> TeamMember:
        """Accept team invitation."""
        # Get invitation
        result = await self.db.execute(
            select(TeamInvitation).where(TeamInvitation.token == token)
        )
        invitation = result.scalar_one_or_none()

        if not invitation or invitation.status != "pending" or invitation.is_expired:
            raise ValueError("Invalid or expired invitation")

        # Create team member
        member = TeamMember(
            team_id=invitation.team_id,
            user_id=user_id,
            role=invitation.role,
        )

        invitation.status = "accepted"
        invitation.accepted_at = datetime.utcnow()

        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        return member

    async def list_teams(self, user_id: uuid.UUID) -> List[Team]:
        """List teams for user."""
        result = await self.db.execute(
            select(Team)
            .join(TeamMember)
            .where(TeamMember.user_id == user_id, Team.is_active == True)
            .order_by(Team.created_at.desc())
        )
        return result.scalars().all()

    async def get_team_members(self, team_id: uuid.UUID) -> List[TeamMember]:
        """Get team members."""
        result = await self.db.execute(
            select(TeamMember).where(TeamMember.team_id == team_id)
        )
        return result.scalars().all()

    async def remove_member(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Remove team member."""
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        member = result.scalar_one_or_none()

        if member and member.role != "owner":
            await self.db.delete(member)
            await self.db.commit()
            return True

        return False
