'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']

export default function AnalyticsPage() {
  const { data: summary } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => apiClient.getUsageSummary(),
  })

  const { data: costBreakdown } = useQuery({
    queryKey: ['cost-breakdown'],
    queryFn: () => apiClient.getCostBreakdown(),
  })

  const { data: dailyStats } = useQuery({
    queryKey: ['daily-stats'],
    queryFn: () => apiClient.getDailyStats(),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Analytics</h1>
        <p className="text-muted-foreground">
          Detailed insights into your usage and costs
        </p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Jobs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_jobs}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Completed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {summary.completed_jobs}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Failed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {summary.failed_jobs}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Cost
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${summary.total_cost.toFixed(2)}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Breakdown by Provider */}
        {costBreakdown && costBreakdown.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Cost by Provider</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={costBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.provider}: $${entry.total_cost.toFixed(2)}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total_cost"
                  >
                    {costBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {/* Job Count by Provider */}
        {costBreakdown && costBreakdown.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Jobs by Provider</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={costBreakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="provider" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="job_count" fill="#3b82f6" name="Jobs" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Daily Statistics */}
      {dailyStats && dailyStats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Daily Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={dailyStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="jobs"
                  stroke="#3b82f6"
                  name="Jobs"
                  strokeWidth={2}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="cost"
                  stroke="#10b981"
                  name="Cost ($)"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Cost Breakdown Table */}
      {costBreakdown && costBreakdown.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Detailed Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Provider</th>
                    <th className="text-left py-3 px-4 font-medium">Model</th>
                    <th className="text-right py-3 px-4 font-medium">Jobs</th>
                    <th className="text-right py-3 px-4 font-medium">Total Cost</th>
                    <th className="text-right py-3 px-4 font-medium">Avg Cost/Job</th>
                  </tr>
                </thead>
                <tbody>
                  {costBreakdown.map((item, index) => (
                    <tr key={index} className="border-b last:border-0">
                      <td className="py-3 px-4">{item.provider}</td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">
                        {item.model}
                      </td>
                      <td className="py-3 px-4 text-right">{item.job_count}</td>
                      <td className="py-3 px-4 text-right font-medium">
                        ${item.total_cost.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right text-sm text-muted-foreground">
                        ${(item.total_cost / item.job_count).toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
