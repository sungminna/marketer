"""Team collaboration schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID


class TeamBase(BaseModel):
    """Base team schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    max_members: Optional[int] = None


class TeamMemberResponse(BaseModel):
    """Team member response."""
    id: UUID
    team_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class TeamResponse(TeamBase):
    """Team response schema."""
    id: UUID
    owner_id: UUID
    max_members: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    member_count: Optional[int] = None

    class Config:
        from_attributes = True


class InviteTeamMemberRequest(BaseModel):
    """Request to invite team member."""
    email: EmailStr = Field(..., description="Email address to invite")
    role: str = Field(default="member", description="Role (member, admin, viewer)")


class TeamInvitationResponse(BaseModel):
    """Team invitation response."""
    id: UUID
    team_id: UUID
    email: str
    role: str
    invited_by: UUID
    token: str
    status: str
    expires_at: datetime
    created_at: datetime
    accepted_at: Optional[datetime]

    class Config:
        from_attributes = True


class AcceptInvitationRequest(BaseModel):
    """Request to accept invitation."""
    token: str = Field(..., description="Invitation token")


class UpdateMemberRoleRequest(BaseModel):
    """Request to update member role."""
    role: str = Field(..., description="New role (admin, member, viewer)")
