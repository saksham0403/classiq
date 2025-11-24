import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analyticsApi } from '../../services/api';
import { getAuth } from '../../utils/auth';
import type { StudentSummary } from '../../types';

export default function StudentSummary() {
  const [summary, setSummary] = useState<StudentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const auth = getAuth();

  useEffect(() => {
    if (auth.user?.id) {
      loadSummary();
    }
  }, [auth.user?.id]);

  const loadSummary = async () => {
    try {
      const data = await analyticsApi.getStudentSummary(auth.user!.id);
      setSummary(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load summary');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!summary) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">No summary data available yet.</p>
          <p className="text-gray-500 text-sm mt-2">Complete some assignments to see your progress.</p>
          <Link to="/student/dashboard" className="text-indigo-600 hover:text-indigo-800 mt-4 inline-block">
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <h1 className="text-xl font-bold text-gray-900 flex items-center">My Learning Summary</h1>
            <Link
              to="/student/dashboard"
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {/* Overall Score */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-semibold mb-2">Overall Performance</h2>
            <div className="text-4xl font-bold text-indigo-600">
              {(summary.overall_score * 100).toFixed(1)}%
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Strengths */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-green-700 mb-4">Strengths</h3>
              {summary.strengths.length === 0 ? (
                <p className="text-gray-500 text-sm">Keep practicing to identify your strengths!</p>
              ) : (
                <ul className="space-y-2">
                  {summary.strengths.map((topic, idx) => (
                    <li key={idx} className="flex items-center">
                      <span className="text-green-600 mr-2">✓</span>
                      <span>{topic}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Weak Topics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-red-700 mb-4">Areas for Improvement</h3>
              {summary.weak_topics.length === 0 ? (
                <p className="text-gray-500 text-sm">Great job! No weak areas identified.</p>
              ) : (
                <ul className="space-y-2">
                  {summary.weak_topics.map((topic, idx) => (
                    <li key={idx} className="flex items-center">
                      <span className="text-red-600 mr-2">⚠</span>
                      <span>{topic}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Recommended Practice */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Recommended Practice</h3>
            {summary.recommended_practice.length === 0 ? (
              <p className="text-gray-500 text-sm">No specific practice recommendations at this time.</p>
            ) : (
              <div className="space-y-3">
                {summary.recommended_practice.map((practice, idx) => (
                  <div key={idx} className="border border-gray-200 rounded p-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-indigo-600">{practice.topic}</span>
                      <span className="text-sm text-gray-500">{practice.type}</span>
                    </div>
                    <p className="text-gray-700">{practice.question_text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

