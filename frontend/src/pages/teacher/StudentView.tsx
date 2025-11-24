import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { classroomApi, analyticsApi } from '../../services/api';
import type { StudentSummary } from '../../types';

export default function StudentView() {
  const { classroomId, studentId } = useParams<{ classroomId: string; studentId: string }>();
  const [student, setStudent] = useState<any>(null);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [summary, setSummary] = useState<StudentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSubmission, setSelectedSubmission] = useState<any | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (classroomId && studentId) {
      loadData();
    }
  }, [classroomId, studentId]);

  const loadData = async () => {
    try {
      const [submissionsData, summaryData] = await Promise.all([
        classroomApi.getStudentSubmissions(Number(classroomId), Number(studentId)),
        analyticsApi.getStudentSummary(Number(studentId))
      ]);
      setStudent(submissionsData.student);
      setSubmissions(submissionsData.submissions);
      setSummary(summaryData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load student data');
    } finally {
      setLoading(false);
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
              <Link
                to={`/teacher/classrooms/${classroomId}`}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back to Classroom
              </Link>
              <h1 className="text-xl font-bold text-gray-900">
                {student?.name || 'Student'}
              </h1>
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

          {student && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{student.name}</h2>
                  <p className="text-gray-600">{student.email}</p>
                </div>
                {summary && (
                  <div className="text-right">
                    <p className="text-3xl font-bold text-indigo-600">
                      {(summary.overall_score * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-500">Overall Score</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Analytics Summary */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Strengths</h3>
                {summary.strengths.length > 0 ? (
                  <div className="space-y-2">
                    {summary.strengths.map((topic, idx) => (
                      <div key={idx} className="bg-green-50 border border-green-200 rounded p-2">
                        <p className="text-sm font-medium text-green-800">{topic}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No strengths identified yet</p>
                )}
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Weak Topics</h3>
                {summary.weak_topics.length > 0 ? (
                  <div className="space-y-2">
                    {summary.weak_topics.map((topic, idx) => (
                      <div key={idx} className="bg-red-50 border border-red-200 rounded p-2">
                        <p className="text-sm font-medium text-red-800">{topic}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No weak topics identified</p>
                )}
              </div>
            </div>
          )}

          {/* Submissions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">
              Assignment Submissions ({submissions.length})
            </h3>
            {selectedSubmission ? (
              <div>
                <button
                  onClick={() => setSelectedSubmission(null)}
                  className="mb-4 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                >
                  ← Back to Submissions List
                </button>
                <div className="border border-gray-200 rounded p-4 mb-4">
                  <h4 className="text-lg font-semibold mb-2">{selectedSubmission.assignment_title}</h4>
                  {selectedSubmission.submitted_at && (
                    <p className="text-sm text-gray-500 mb-2">
                      Submitted: {new Date(selectedSubmission.submitted_at).toLocaleString()}
                    </p>
                  )}
                  <div className="text-right">
                    <p className="text-2xl font-bold text-indigo-600">
                      {(selectedSubmission.score * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-500">Score</p>
                  </div>
                </div>
                <div className="space-y-4">
                  {selectedSubmission.answers.map((answer: any, idx: number) => (
                    <div
                      key={answer.question_id}
                      className={`border rounded p-4 ${
                        answer.ai_is_correct
                          ? 'border-green-300 bg-green-50'
                          : 'border-red-300 bg-red-50'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium">Question {idx + 1}</span>
                        <span
                          className={`font-semibold ${
                            answer.ai_is_correct ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {answer.ai_is_correct ? '✓ Correct' : '✗ Incorrect'} ({(answer.ai_score * 100).toFixed(1)}%)
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2 font-medium">{answer.question_text}</p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                        <div>
                          <p className="text-sm font-semibold text-gray-600 mb-1">Student Answer:</p>
                          <p className="text-gray-800 bg-white p-2 rounded border">{answer.student_answer}</p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-600 mb-1">Correct Answer:</p>
                          <p className="text-gray-800 bg-white p-2 rounded border">{answer.correct_answer}</p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        Type: {answer.question_type} • Topic: {answer.topic_tag}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ) : submissions.length === 0 ? (
              <p className="text-gray-500">No submissions yet.</p>
            ) : (
              <div className="space-y-2">
                {submissions.map((submission) => (
                  <button
                    key={submission.submission_id}
                    onClick={() => setSelectedSubmission(submission)}
                    className="w-full text-left p-4 border border-gray-200 rounded hover:bg-gray-50 hover:border-indigo-300 transition"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{submission.assignment_title}</p>
                        {submission.submitted_at && (
                          <p className="text-sm text-gray-500">
                            {new Date(submission.submitted_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-indigo-600">
                          {(submission.score * 100).toFixed(1)}%
                        </p>
                        <p className="text-xs text-gray-500">Score</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

