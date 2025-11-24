import axios from 'axios';
import type { 
  Token, 
  LoginRequest, 
  UserCreate, 
  Classroom, 
  ClassroomCreate,
  AddStudentRequest,
  Assignment,
  AssignmentCreate,
  QuestionCreate,
  AssignmentWithQuestions,
  SubmissionCreate,
  SubmissionResponse,
  ClassroomAnalytics,
  StudentSummary
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const authApi = {
  signup: async (data: UserCreate): Promise<Token> => {
    const response = await api.post<Token>('/auth/signup', data);
    return response.data;
  },
  login: async (data: LoginRequest): Promise<Token> => {
    const response = await api.post<Token>('/auth/login', data);
    return response.data;
  },
};

// Classrooms
export const classroomApi = {
  create: async (data: ClassroomCreate): Promise<Classroom> => {
    const response = await api.post<Classroom>('/classrooms/', data);
    return response.data;
  },
  list: async (): Promise<Classroom[]> => {
    const response = await api.get<Classroom[]>('/classrooms/');
    return response.data;
  },
  addStudent: async (classroomId: number, data: AddStudentRequest): Promise<void> => {
    await api.post(`/classrooms/${classroomId}/students`, data);
  },
  listStudents: async (classroomId: number) => {
    const response = await api.get(`/classrooms/${classroomId}/students`);
    return response.data;
  },
  getStudentSubmissions: async (classroomId: number, studentId: number) => {
    const response = await api.get(`/classrooms/${classroomId}/students/${studentId}/submissions`);
    return response.data;
  },
};

// Assignments
export const assignmentApi = {
  create: async (data: AssignmentCreate): Promise<Assignment> => {
    const response = await api.post<Assignment>('/assignments/', data);
    return response.data;
  },
  listByClassroom: async (classroomId: number): Promise<Assignment[]> => {
    const response = await api.get<Assignment[]>(`/classrooms/${classroomId}/assignments`);
    return response.data;
  },
  get: async (assignmentId: number): Promise<AssignmentWithQuestions> => {
    const response = await api.get<AssignmentWithQuestions>(`/assignments/${assignmentId}`);
    return response.data;
  },
  addQuestion: async (assignmentId: number, data: QuestionCreate) => {
    const response = await api.post(`/assignments/${assignmentId}/questions`, data);
    return response.data;
  },
  updateStatus: async (assignmentId: number, status: 'draft' | 'open' | 'graded'): Promise<Assignment> => {
    const response = await api.patch<Assignment>(`/assignments/${assignmentId}/status`, { status });
    return response.data;
  },
  getSubmissions: async (assignmentId: number) => {
    const response = await api.get(`/assignments/${assignmentId}/submissions`);
    return response.data;
  },
  getSubmission: async (assignmentId: number, submissionId: number) => {
    const response = await api.get(`/assignments/${assignmentId}/submissions/${submissionId}`);
    return response.data;
  },
};

// Submissions
export const submissionApi = {
  submit: async (assignmentId: number, data: SubmissionCreate): Promise<SubmissionResponse> => {
    const response = await api.post<SubmissionResponse>(`/assignments/${assignmentId}/submissions`, data);
    return response.data;
  },
};

// Students
export const studentApi = {
  getMyAssignments: async (): Promise<Assignment[]> => {
    const response = await api.get<Assignment[]>(`/students/me/assignments`);
    return response.data;
  },
};

// Analytics
export const analyticsApi = {
  getClassroomAnalytics: async (classroomId: number): Promise<ClassroomAnalytics> => {
    const response = await api.get<ClassroomAnalytics>(`/classrooms/${classroomId}/analytics`);
    return response.data;
  },
  getStudentSummary: async (studentId: number): Promise<StudentSummary> => {
    const response = await api.get<StudentSummary>(`/students/${studentId}/summary`);
    return response.data;
  },
};

