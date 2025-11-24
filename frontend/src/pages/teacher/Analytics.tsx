import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { analyticsApi } from '../../services/api';
import type { ClassroomAnalytics } from '../../types';

export default function TeacherAnalytics() {
  const { classroomId } = useParams<{ classroomId: string }>();
  const [analytics, setAnalytics] = useState<ClassroomAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAnalytics();
  }, [classroomId]);

  const loadAnalytics = async () => {
    try {
      const data = await analyticsApi.getClassroomAnalytics(Number(classroomId));
      setAnalytics(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!analytics) {
    return <div className="flex items-center justify-center min-h-screen">No analytics data</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <h1 className="text-xl font-bold text-gray-900 flex items-center">Classroom Analytics</h1>
            <Link
              to={`/teacher/classrooms/${classroomId}`}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* Assignment Summary */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Assignment Summary</h2>
            <div className="space-y-2">
              {analytics.assignment_summary.map((assignment) => (
                <div key={assignment.assignment_id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span className="font-medium">{assignment.title}</span>
                  <span className="text-indigo-600 font-semibold">
                    {(assignment.avg_score * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Topic Performance Chart */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Topic Performance</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.topics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="topic" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
                <Legend />
                <Bar dataKey="accuracy" fill="#4F46E5" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Hardest Questions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Hardest Questions</h2>
            <div className="space-y-3">
              {analytics.hardest_questions.map((question) => (
                <div key={question.question_id} className="border border-gray-200 rounded p-4">
                  <p className="text-gray-700 mb-2">{question.text}</p>
                  <p className="text-sm text-red-600 font-semibold">
                    {(question.percent_correct * 100).toFixed(1)}% correct
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

