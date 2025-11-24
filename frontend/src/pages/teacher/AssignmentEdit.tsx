import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assignmentApi } from '../../services/api';
import type { AssignmentWithQuestions, QuestionCreate } from '../../types';

export default function TeacherAssignmentEdit() {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const [assignment, setAssignment] = useState<AssignmentWithQuestions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [questionText, setQuestionText] = useState('');
  const [correctAnswer, setCorrectAnswer] = useState('');
  const [questionType, setQuestionType] = useState<'numeric' | 'algebra' | 'short_answer' | 'mcq'>('numeric');
  const [topicTag, setTopicTag] = useState('');
  const [addingQuestion, setAddingQuestion] = useState(false);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [selectedSubmission, setSelectedSubmission] = useState<any | null>(null);
  const [loadingSubmissions, setLoadingSubmissions] = useState(false);
  const [loadingSubmission, setLoadingSubmission] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadAssignment();
    if (assignmentId) {
      loadSubmissions();
    }
  }, [assignmentId]);

  const loadAssignment = async () => {
    try {
      const data = await assignmentApi.get(Number(assignmentId));
      setAssignment(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load assignment');
    } finally {
      setLoading(false);
    }
  };

  const loadSubmissions = async () => {
    if (!assignmentId) return;
    setLoadingSubmissions(true);
    try {
      const data = await assignmentApi.getSubmissions(Number(assignmentId));
      setSubmissions(data);
    } catch (err: any) {
      console.error('Failed to load submissions:', err);
    } finally {
      setLoadingSubmissions(false);
    }
  };

  const handleViewSubmission = async (submissionId: number) => {
    if (!assignmentId) return;
    setLoadingSubmission(true);
    try {
      const data = await assignmentApi.getSubmission(Number(assignmentId), submissionId);
      setSelectedSubmission(data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to load submission');
    } finally {
      setLoadingSubmission(false);
    }
  };

  const handleAddQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignmentId) return;

    setAddingQuestion(true);
    try {
      await assignmentApi.addQuestion(Number(assignmentId), {
        text: questionText,
        correct_answer: correctAnswer,
        question_type: questionType,
        topic_tag: topicTag,
      });
      setQuestionText('');
      setCorrectAnswer('');
      setTopicTag('');
      loadAssignment();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to add question');
    } finally {
      setAddingQuestion(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!assignment) {
    return <div className="flex items-center justify-center min-h-screen">Assignment not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <h1 className="text-xl font-bold text-gray-900 flex items-center">{assignment.title}</h1>
            <button
              onClick={() => navigate(-1)}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back
            </button>
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

          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-lg font-semibold mb-2">{assignment.title}</h2>
                {assignment.description && (
                  <p className="text-gray-600 mb-2">{assignment.description}</p>
                )}
                <p className="text-sm text-gray-500">
                  Status: <span className={`font-semibold ${
                    assignment.status === 'open' ? 'text-green-600' :
                    assignment.status === 'graded' ? 'text-blue-600' :
                    'text-gray-600'
                  }`}>{assignment.status.toUpperCase()}</span>
                </p>
              </div>
              <div className="flex flex-col gap-2">
                {assignment.status === 'draft' && (
                  <button
                    onClick={async () => {
                      if (assignment.questions.length === 0) {
                        alert('Please add at least one question before opening the assignment');
                        return;
                      }
                      if (confirm('Open this assignment? Students will be able to submit answers.')) {
                        try {
                          await assignmentApi.updateStatus(Number(assignmentId), 'open');
                          await loadAssignment();
                        } catch (err: any) {
                          alert(err.response?.data?.detail || 'Failed to update status');
                        }
                      }
                    }}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm font-medium"
                  >
                    Open Assignment
                  </button>
                )}
                {assignment.status === 'open' && (
                  <button
                    onClick={async () => {
                      if (confirm('Mark this assignment as graded? This will close it for new submissions.')) {
                        try {
                          await assignmentApi.updateStatus(Number(assignmentId), 'graded');
                          await loadAssignment();
                        } catch (err: any) {
                          alert(err.response?.data?.detail || 'Failed to update status');
                        }
                      }
                    }}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm font-medium"
                  >
                    Mark as Graded
                  </button>
                )}
                {assignment.status === 'graded' && (
                  <button
                    onClick={async () => {
                      if (confirm('Reopen this assignment? Students will be able to submit again.')) {
                        try {
                          await assignmentApi.updateStatus(Number(assignmentId), 'open');
                          await loadAssignment();
                        } catch (err: any) {
                          alert(err.response?.data?.detail || 'Failed to update status');
                        }
                      }
                    }}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 text-sm font-medium"
                  >
                    Reopen Assignment
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Add Question Form */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Add Question</h3>
            <form onSubmit={handleAddQuestion} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Question Text</label>
                <textarea
                  required
                  value={questionText}
                  onChange={(e) => setQuestionText(e.target.value)}
                  rows={3}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Correct Answer</label>
                <input
                  type="text"
                  required
                  value={correctAnswer}
                  onChange={(e) => setCorrectAnswer(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Question Type</label>
                  <select
                    value={questionType}
                    onChange={(e) => setQuestionType(e.target.value as any)}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="numeric">Numeric</option>
                    <option value="algebra">Algebra</option>
                    <option value="short_answer">Short Answer</option>
                    <option value="mcq">Multiple Choice</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Topic Tag</label>
                  <input
                    type="text"
                    required
                    value={topicTag}
                    onChange={(e) => setTopicTag(e.target.value)}
                    placeholder="e.g., Factoring Quadratics"
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={addingQuestion}
                className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
              >
                {addingQuestion ? 'Adding...' : 'Add Question'}
              </button>
            </form>
          </div>

          {/* Questions List */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Questions ({assignment.questions.length})</h3>
            {assignment.questions.length === 0 ? (
              <p className="text-gray-500">No questions yet. Add your first question above.</p>
            ) : (
              <div className="space-y-4">
                {assignment.questions.map((q, idx) => (
                  <div key={q.id} className="border border-gray-200 rounded p-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium">Question {idx + 1}</span>
                      <span className="text-sm text-gray-500">{q.question_type} • {q.topic_tag}</span>
                    </div>
                    <p className="text-gray-700 mb-2">{q.text}</p>
                    <p className="text-sm text-gray-500">Correct Answer: {q.correct_answer}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submissions Section */}
          {(assignment.status === 'open' || assignment.status === 'graded') && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">
                Student Submissions ({submissions.length})
              </h3>
              {loadingSubmissions ? (
                <p className="text-gray-500">Loading submissions...</p>
              ) : submissions.length === 0 ? (
                <p className="text-gray-500">No submissions yet.</p>
              ) : selectedSubmission ? (
                <div>
                  <button
                    onClick={() => setSelectedSubmission(null)}
                    className="mb-4 text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                  >
                    ← Back to Submissions List
                  </button>
                  <div className="border border-gray-200 rounded p-4 mb-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="text-lg font-semibold">{selectedSubmission.student.name}</h4>
                        <p className="text-sm text-gray-500">{selectedSubmission.student.email}</p>
                        {selectedSubmission.submitted_at && (
                          <p className="text-sm text-gray-500">
                            Submitted: {new Date(selectedSubmission.submitted_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-indigo-600">
                          {(selectedSubmission.total_score * 100).toFixed(1)}%
                        </p>
                        <p className="text-sm text-gray-500">Overall Score</p>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    {selectedSubmission.answers.map((answer: any, idx: number) => {
                      const question = assignment.questions.find(q => q.id === answer.question_id);
                      return (
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
                          <p className="text-gray-700 mb-2 font-medium">{answer.question_text || question?.text}</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                            <div>
                              <p className="text-sm font-semibold text-gray-600 mb-1">Student Answer:</p>
                              <p className="text-gray-800 bg-white p-2 rounded border">{answer.student_answer}</p>
                            </div>
                            <div>
                              <p className="text-sm font-semibold text-gray-600 mb-1">Correct Answer:</p>
                              <p className="text-gray-800 bg-white p-2 rounded border">{answer.correct_answer || question?.correct_answer}</p>
                            </div>
                          </div>
                          <p className="text-xs text-gray-500 mt-2">
                            Type: {answer.question_type} • Topic: {answer.topic_tag || question?.topic_tag}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  {submissions.map((submission) => (
                    <button
                      key={submission.submission_id}
                      onClick={() => handleViewSubmission(submission.submission_id)}
                      className="w-full text-left p-4 border border-gray-200 rounded hover:bg-gray-50 hover:border-indigo-300 transition"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-gray-900">{submission.student.name}</p>
                          <p className="text-sm text-gray-500">{submission.student.email}</p>
                          {submission.submitted_at && (
                            <p className="text-xs text-gray-400 mt-1">
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
          )}
        </div>
      </main>
    </div>
  );
}

