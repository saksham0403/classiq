import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getAuth, clearAuth } from '../../utils/auth';
import { studentApi } from '../../services/api';
import type { Assignment } from '../../types';

export default function StudentDashboard() {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const auth = getAuth();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const assignmentsData = await studentApi.getMyAssignments();
      setAssignments(assignmentsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">ClassIQ</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {auth.user?.name}</span>
              <Link
                to="/student/summary"
                className="text-indigo-600 hover:text-indigo-800"
              >
                My Summary
              </Link>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
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

          <h2 className="text-2xl font-bold text-gray-900 mb-6">My Assignments</h2>

          {assignments.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No assignments available yet.</p>
              <p className="text-gray-500 text-sm mt-2">Your teacher will add assignments to your classrooms.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {assignments.map((assignment) => (
                <Link
                  key={assignment.id}
                  to={`/student/assignments/${assignment.id}`}
                  className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
                >
                  <h3 className="text-lg font-semibold text-gray-900">{assignment.title}</h3>
                  {assignment.description && (
                    <p className="text-gray-600 mt-2">{assignment.description}</p>
                  )}
                  {assignment.due_date && (
                    <p className="text-sm text-gray-500 mt-2">
                      Due: {new Date(assignment.due_date).toLocaleDateString()}
                    </p>
                  )}
                  <p className="text-sm text-indigo-600 mt-2">Click to view and submit →</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

