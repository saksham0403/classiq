import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { classroomApi } from '../../services/api';
import { getAuth, clearAuth } from '../../utils/auth';
import type { Classroom } from '../../types';

export default function TeacherDashboard() {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const auth = getAuth();

  useEffect(() => {
    loadClassrooms();
  }, []);

  const loadClassrooms = async () => {
    try {
      const data = await classroomApi.list();
      setClassrooms(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load classrooms');
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
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">My Classrooms</h2>
            <button
              onClick={async () => {
                const name = prompt('Enter classroom name:');
                if (name && name.trim()) {
                  setCreating(true);
                  setError('');
                  try {
                    await classroomApi.create({ name: name.trim() });
                    await loadClassrooms();
                  } catch (err: any) {
                    setError(err.response?.data?.detail || 'Failed to create classroom');
                  } finally {
                    setCreating(false);
                  }
                } else if (name !== null) {
                  setError('Classroom name cannot be empty');
                }
              }}
              disabled={creating}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {creating ? 'Creating...' : 'Create Classroom'}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {classrooms.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No classrooms yet. Create your first classroom!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {classrooms.map((classroom) => (
                <Link
                  key={classroom.id}
                  to={`/teacher/classrooms/${classroom.id}`}
                  className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
                >
                  <h3 className="text-lg font-semibold text-gray-900">{classroom.name}</h3>
                  <p className="text-sm text-gray-500 mt-2">Click to view details</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

