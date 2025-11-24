import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { classroomApi, assignmentApi } from '../../services/api';
import { clearAuth } from '../../utils/auth';
import type { Classroom, Assignment } from '../../types';

export default function TeacherClassroom() {
  const { classroomId } = useParams<{ classroomId: string }>();
  const [classroom, setClassroom] = useState<Classroom | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (classroomId) {
      loadData();
    }
  }, [classroomId]);

  const loadData = async () => {
    try {
      const [classroomsData, assignmentsData, studentsData] = await Promise.all([
        classroomApi.list(),
        assignmentApi.listByClassroom(Number(classroomId)),
        classroomApi.listStudents(Number(classroomId))
      ]);
      const currentClassroom = classroomsData.find(c => c.id === Number(classroomId));
      if (currentClassroom) {
        setClassroom(currentClassroom);
      }
      setAssignments(assignmentsData);
      setStudents(studentsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = async () => {
    const email = prompt('Enter student email:');
    if (email && classroomId) {
      try {
        await classroomApi.addStudent(Number(classroomId), { student_email: email });
        loadData();
      } catch (err: any) {
        alert(err.response?.data?.detail || 'Failed to add student');
      }
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link to="/teacher/dashboard" className="text-gray-600 hover:text-gray-900">
                ← Back
              </Link>
              <h1 className="text-xl font-bold text-gray-900">
                {classroom?.name || 'Classroom'}
              </h1>
            </div>
            <button
              onClick={() => {
                clearAuth();
                navigate('/login');
              }}
              className="text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
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

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Students Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Students ({students.length})</h2>
                <button
                  onClick={handleAddStudent}
                  className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                >
                  Add Student
                </button>
              </div>
              <div className="space-y-2">
                {students.length === 0 ? (
                  <p className="text-gray-500 text-sm">No students enrolled yet</p>
                ) : (
                  students.map((student) => (
                    <Link
                      key={student.id}
                      to={`/teacher/classrooms/${classroomId}/students/${student.student.id}`}
                      className="block p-3 bg-gray-50 rounded hover:bg-gray-100 hover:border-indigo-300 border border-transparent transition"
                    >
                      <p className="font-medium text-gray-900">{student.student.name}</p>
                      <p className="text-sm text-gray-500">{student.student.email}</p>
                    </Link>
                  ))
                )}
              </div>
            </div>

            {/* Assignments Section */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Assignments ({assignments.length})</h2>
                <Link
                  to={`/teacher/assignments/new?classroomId=${classroomId}`}
                  className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                >
                  Create Assignment
                </Link>
              </div>
              <div className="space-y-2">
                {assignments.length === 0 ? (
                  <p className="text-gray-500 text-sm">No assignments yet</p>
                ) : (
                  assignments.map((assignment) => (
                    <Link
                      key={assignment.id}
                      to={`/teacher/assignments/${assignment.id}/edit`}
                      className="block p-3 bg-gray-50 rounded hover:bg-gray-100"
                    >
                      <p className="font-medium">{assignment.title}</p>
                      <p className="text-sm text-gray-500">Status: {assignment.status}</p>
                    </Link>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="mt-6">
            <Link
              to={`/teacher/analytics/${classroomId}`}
              className="inline-block bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              View Analytics
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}

