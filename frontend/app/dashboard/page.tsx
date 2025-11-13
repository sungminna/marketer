'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Image, Video, DollarSign, CheckCircle, Clock, XCircle, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { formatDistanceToNow } from 'date-fns'

export default function DashboardPage() {
  const { data: summary } = useQuery({
    queryKey: ['usage-summary'],
    queryFn: () => apiClient.getUsageSummary(),
  })

  const { data: recentJobs } = useQuery({
    queryKey: ['recent-jobs'],
    queryFn: () => apiClient.listImageJobs(1, 5),
  })

  const { data: quota } = useQuery({
    queryKey: ['quota'],
    queryFn: () => apiClient.getQuotaUsage(),
  })

  const stats = [
    {
      name: 'Total Jobs',
      value: summary?.total_jobs || 0,
      icon: Clock,
      description: 'All time',
    },
    {
      name: 'Completed',
      value: summary?.completed_jobs || 0,
      icon: CheckCircle,
      description: 'Successfully processed',
    },
    {
      name: 'Total Cost',
      value: `$${summary?.total_cost.toFixed(2) || '0.00'}`,
      icon: DollarSign,
      description: 'Lifetime spend',
    },
    {
      name: 'Failed',
      value: summary?.failed_jobs || 0,
      icon: XCircle,
      description: 'Needs attention',
    },
  ]

  const quickActions = [
    {
      name: 'Generate Image',
      description: 'Create AI-generated images',
      href: '/dashboard/images',
      icon: Image,
      color: 'text-blue-500',
    },
    {
      name: 'Generate Video',
      description: 'Create AI-generated videos',
      href: '/dashboard/videos',
      icon: Video,
      color: 'text-purple-500',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here&apos;s your overview.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.name}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quota Usage */}
      {quota && (
        <Card>
          <CardHeader>
            <CardTitle>Quota Usage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Jobs</span>
                <span className="text-sm text-muted-foreground">
                  {quota.jobs_used} / {quota.jobs_limit}
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${(quota.jobs_used / quota.jobs_limit) * 100}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Cost</span>
                <span className="text-sm text-muted-foreground">
                  ${quota.cost_used.toFixed(2)} / ${quota.cost_limit.toFixed(2)}
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{ width: `${(quota.cost_used / quota.cost_limit) * 100}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {quickActions.map((action) => (
              <Link key={action.name} href={action.href}>
                <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors cursor-pointer">
                  <div className="flex items-center space-x-3">
                    <action.icon className={`w-6 h-6 ${action.color}`} />
                    <div>
                      <p className="font-medium">{action.name}</p>
                      <p className="text-sm text-muted-foreground">{action.description}</p>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-muted-foreground" />
                </div>
              </Link>
            ))}
          </CardContent>
        </Card>

        {/* Recent Jobs */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Jobs</CardTitle>
            <Link href="/dashboard/jobs">
              <Button variant="ghost" size="sm">
                View all
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentJobs?.items.map((job) => (
                <div key={job.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium truncate">{job.prompt || job.job_type}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  <Badge
                    variant={
                      job.status === 'completed'
                        ? 'success'
                        : job.status === 'failed'
                        ? 'destructive'
                        : 'secondary'
                    }
                  >
                    {job.status}
                  </Badge>
                </div>
              ))}
              {(!recentJobs?.items || recentJobs.items.length === 0) && (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No recent jobs found
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
