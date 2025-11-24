import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { assignmentApi, submissionApi } from '../../services/api';
import { getAuth } from '../../utils/auth';
import type { AssignmentWithQuestions, AnswerSubmission, SubmissionResponse } from '../../types';

export default function StudentAssignment() {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const [assignment, setAssignment] = useState<AssignmentWithQuestions | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submission, setSubmission] = useState<SubmissionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const auth = getAuth();

  useEffect(() => {
    loadAssignment();
  }, [assignmentId]);

  const loadAssignment = async () => {
    try {
      const data = await assignmentApi.get(Number(assignmentId));
      setAssignment(data);
      // Initialize answers object
      const initialAnswers: Record<number, string> = {};
      data.questions.forEach((q) => {
        initialAnswers[q.id] = '';
      });
      setAnswers(initialAnswers);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load assignment');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignmentId) return;

    setSubmitting(true);
    setError('');

    try {
      const answerSubmissions: AnswerSubmission[] = assignment!.questions.map((q) => ({
        question_id: q.id,
        student_answer: answers[q.id] || '',
      }));

      const result = await submissionApi.submit(Number(assignmentId), {
        answers: answerSubmissions,
      });
      setSubmission(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit assignment');
    } finally {
      setSubmitting(false);
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
              onClick={() => navigate('/student/dashboard')}
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
            <h2 className="text-lg font-semibold mb-2">{assignment.title}</h2>
            {assignment.description && (
              <p className="text-gray-600 mb-2">{assignment.description}</p>
            )}
            {assignment.due_date && (
              <p className="text-sm text-gray-500">
                Due: {new Date(assignment.due_date).toLocaleString()}
              </p>
            )}
          </div>

          {submission ? (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="mb-4">
                <h3 className="text-xl font-semibold mb-2">Submission Results</h3>
                <p className="text-lg">
                  Your Score: <span className="font-bold text-indigo-600">
                    {(submission.total_score * 100).toFixed(1)}%
                  </span>
                </p>
              </div>

              <div className="space-y-4">
                {submission.answers.map((answer, idx) => {
                  const question = assignment.questions.find((q) => q.id === answer.question_id);
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
                          {answer.ai_is_correct ? '✓ Correct' : '✗ Incorrect'}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2">{question?.text}</p>
                      <p className="text-sm text-gray-600 mb-1">
                        <strong>Your answer:</strong> {answer.student_answer}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong>Correct answer:</strong> {answer.correct_answer}
                      </p>
                      <p className="text-sm text-gray-500 mt-2">
                        Score: {(answer.ai_score * 100).toFixed(1)}%
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
              <div className="space-y-6">
                {assignment.questions.map((question, idx) => (
                  <div key={question.id} className="border border-gray-200 rounded p-4">
                    <div className="mb-2">
                      <span className="font-medium">Question {idx + 1}</span>
                      <span className="text-sm text-gray-500 ml-2">
                        ({question.question_type} • {question.topic_tag})
                      </span>
                    </div>
                    <p className="text-gray-700 mb-3">{question.text}</p>
                    <textarea
                      required
                      value={answers[question.id] || ''}
                      onChange={(e) =>
                        setAnswers({ ...answers, [question.id]: e.target.value })
                      }
                      rows={3}
                      placeholder="Enter your answer..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                ))}
              </div>

              <div className="mt-6">
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
                >
                  {submitting ? 'Submitting...' : 'Submit Assignment'}
                </button>
              </div>
            </form>
          )}
        </div>
      </main>
    </div>
  );
}

