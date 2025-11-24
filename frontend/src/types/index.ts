export interface User {
  id: number;
  name: string;
  email: string;
  role: "teacher" | "student";
  created_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface UserCreate {
  name: string;
  email: string;
  password: string;
  role: "teacher" | "student";
}

export interface ClassroomCreate {
  name: string;
}

export interface AddStudentRequest {
  student_email: string;
}

export interface AssignmentCreate {
  classroom_id: number;
  title: string;
  description?: string;
  due_date?: string;
}

export interface QuestionCreate {
  text: string;
  correct_answer: string;
  question_type: "numeric" | "algebra" | "short_answer" | "mcq";
  topic_tag: string;
}

export interface SubmissionCreate {
  answers: AnswerSubmission[];
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Classroom {
  id: number;
  name: string;
  teacher_id: number;
  created_at?: string;
}

export interface Assignment {
  id: number;
  classroom_id: number;
  title: string;
  description?: string;
  status: "draft" | "open" | "graded";
  created_at?: string;
  due_date?: string;
}

export interface Question {
  id: number;
  assignment_id: number;
  text: string;
  correct_answer: string;
  question_type: "numeric" | "algebra" | "short_answer" | "mcq";
  topic_tag: string;
}

export interface AssignmentWithQuestions extends Assignment {
  questions: Question[];
}

export interface AnswerSubmission {
  question_id: number;
  student_answer: string;
}

export interface AnswerResponse {
  question_id: number;
  student_answer: string;
  correct_answer: string;
  ai_is_correct: boolean;
  ai_score: number;
  feedback?: string;
}

export interface SubmissionResponse {
  submission_id: number;
  total_score: number;
  answers: AnswerResponse[];
}

export interface ClassroomAnalytics {
  assignment_summary: AssignmentSummary[];
  topics: TopicPerformance[];
  hardest_questions: HardestQuestion[];
}

export interface AssignmentSummary {
  assignment_id: number;
  title: string;
  avg_score: number;
}

export interface TopicPerformance {
  topic: string;
  accuracy: number;
}

export interface HardestQuestion {
  question_id: number;
  text: string;
  percent_correct: number;
}

export interface StudentSummary {
  overall_score: number;
  strengths: string[];
  weak_topics: string[];
  recommended_practice: RecommendedPractice[];
}

export interface RecommendedPractice {
  topic: string;
  question_text: string;
  type: string;
}

