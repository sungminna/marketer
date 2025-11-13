'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Plus, Users as UsersIcon, Mail, Trash2, Crown, Shield, User } from 'lucide-react'

const teamSchema = z.object({
  name: z.string().min(2, 'Team name must be at least 2 characters'),
})

const inviteSchema = z.object({
  email: z.string().email('Invalid email address'),
  role: z.enum(['admin', 'member']),
})

type TeamFormData = z.infer<typeof teamSchema>
type InviteFormData = z.infer<typeof inviteSchema>

export default function TeamsPage() {
  const queryClient = useQueryClient()
  const [showCreateTeam, setShowCreateTeam] = useState(false)
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null)
  const [showInvite, setShowInvite] = useState(false)

  const { data: teams, isLoading: teamsLoading } = useQuery({
    queryKey: ['teams'],
    queryFn: () => apiClient.listTeams(),
  })

  const { data: members, isLoading: membersLoading } = useQuery({
    queryKey: ['team-members', selectedTeam],
    queryFn: () => apiClient.getTeamMembers(selectedTeam!),
    enabled: !!selectedTeam,
  })

  const {
    register: registerTeam,
    handleSubmit: handleSubmitTeam,
    reset: resetTeam,
    formState: { errors: teamErrors },
  } = useForm<TeamFormData>({
    resolver: zodResolver(teamSchema),
  })

  const {
    register: registerInvite,
    handleSubmit: handleSubmitInvite,
    reset: resetInvite,
    formState: { errors: inviteErrors },
  } = useForm<InviteFormData>({
    resolver: zodResolver(inviteSchema),
    defaultValues: {
      role: 'member',
    },
  })

  const createTeamMutation = useMutation({
    mutationFn: (data: TeamFormData) => apiClient.createTeam(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['teams'] })
      setShowCreateTeam(false)
      setSelectedTeam(data.id)
      resetTeam()
    },
  })

  const inviteMutation = useMutation({
    mutationFn: (data: InviteFormData) =>
      apiClient.inviteTeamMember(selectedTeam!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['team-members'] })
      setShowInvite(false)
      resetInvite()
    },
  })

  const removeMemberMutation = useMutation({
    mutationFn: ({ teamId, memberId }: { teamId: string; memberId: string }) =>
      apiClient.removeTeamMember(teamId, memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['team-members'] })
    },
  })

  const onCreateTeam = (data: TeamFormData) => {
    createTeamMutation.mutate(data)
  }

  const onInviteMember = (data: InviteFormData) => {
    inviteMutation.mutate(data)
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner':
        return <Crown className="w-4 h-4 text-yellow-500" />
      case 'admin':
        return <Shield className="w-4 h-4 text-blue-500" />
      default:
        return <User className="w-4 h-4 text-gray-500" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Teams</h1>
          <p className="text-muted-foreground">
            Collaborate with your team members
          </p>
        </div>
        <Button onClick={() => setShowCreateTeam(!showCreateTeam)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Team
        </Button>
      </div>

      {/* Create Team Form */}
      {showCreateTeam && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Team</CardTitle>
            <CardDescription>
              Start collaborating with your colleagues
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmitTeam(onCreateTeam)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Team Name</Label>
                <Input
                  id="name"
                  placeholder="Marketing Team"
                  {...registerTeam('name')}
                />
                {teamErrors.name && (
                  <p className="text-sm text-red-500">{teamErrors.name.message}</p>
                )}
              </div>

              <div className="flex space-x-2">
                <Button type="submit" disabled={createTeamMutation.isPending}>
                  {createTeamMutation.isPending ? 'Creating...' : 'Create Team'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateTeam(false)
                    resetTeam()
                  }}
                >
                  Cancel
                </Button>
              </div>

              {createTeamMutation.isError && (
                <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                  {(createTeamMutation.error as any)?.response?.data?.detail ||
                    'Failed to create team. Please try again.'}
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      )}

      <Tabs value={selectedTeam || teams?.[0]?.id || ''} onValueChange={setSelectedTeam}>
        <TabsList>
          {teams?.map((team) => (
            <TabsTrigger key={team.id} value={team.id}>
              {team.name}
            </TabsTrigger>
          ))}
          {(!teams || teams.length === 0) && <TabsTrigger value="">No Teams</TabsTrigger>}
        </TabsList>

        {teams?.map((team) => (
          <TabsContent key={team.id} value={team.id} className="mt-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium">{team.name}</h3>
                <p className="text-sm text-muted-foreground">
                  Manage team members and permissions
                </p>
              </div>
              <Button onClick={() => setShowInvite(!showInvite)} size="sm">
                <Mail className="w-4 h-4 mr-2" />
                Invite Member
              </Button>
            </div>

            {/* Invite Member Form */}
            {showInvite && (
              <Card>
                <CardHeader>
                  <CardTitle>Invite Team Member</CardTitle>
                  <CardDescription>
                    Send an invitation to join {team.name}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmitInvite(onInviteMember)} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="colleague@example.com"
                        {...registerInvite('email')}
                      />
                      {inviteErrors.email && (
                        <p className="text-sm text-red-500">{inviteErrors.email.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="role">Role</Label>
                      <select
                        id="role"
                        {...registerInvite('role')}
                        className="w-full h-9 rounded-md border border-input bg-transparent px-3 py-1 text-sm"
                      >
                        <option value="member">Member</option>
                        <option value="admin">Admin</option>
                      </select>
                    </div>

                    <div className="flex space-x-2">
                      <Button type="submit" disabled={inviteMutation.isPending}>
                        {inviteMutation.isPending ? 'Sending...' : 'Send Invitation'}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setShowInvite(false)
                          resetInvite()
                        }}
                      >
                        Cancel
                      </Button>
                    </div>

                    {inviteMutation.isError && (
                      <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                        {(inviteMutation.error as any)?.response?.data?.detail ||
                          'Failed to send invitation. Please try again.'}
                      </div>
                    )}
                  </form>
                </CardContent>
              </Card>
            )}

            {/* Team Members */}
            <Card>
              <CardHeader>
                <CardTitle>Team Members</CardTitle>
              </CardHeader>
              <CardContent>
                {membersLoading ? (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    Loading members...
                  </p>
                ) : members && members.length > 0 ? (
                  <div className="space-y-3">
                    {members.map((member) => (
                      <div
                        key={member.id}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <UsersIcon className="w-5 h-5 text-muted-foreground" />
                          <div>
                            <div className="flex items-center space-x-2">
                              <p className="font-medium">User {member.user_id.slice(0, 8)}</p>
                              {getRoleIcon(member.role)}
                              <Badge variant="outline" className="text-xs capitalize">
                                {member.role}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Joined {new Date(member.joined_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        {member.role !== 'owner' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              removeMemberMutation.mutate({
                                teamId: team.id,
                                memberId: member.id,
                              })
                            }
                            disabled={removeMemberMutation.isPending}
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <UsersIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-sm text-muted-foreground">
                      No team members yet. Invite someone to join!
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}

        {(!teams || teams.length === 0) && (
          <TabsContent value="">
            <Card>
              <CardContent className="py-12">
                <div className="text-center">
                  <UsersIcon className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-sm text-muted-foreground mb-4">
                    You haven&apos;t created any teams yet.
                  </p>
                  <Button onClick={() => setShowCreateTeam(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Your First Team
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
