import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import HomePage from './pages/HomePage';
import Login from './pages/Login';
import Signup from './pages/Signup';
import TeacherDashboard from './pages/teacher/Dashboard';
import TeacherClassroom from './pages/teacher/Classroom';
import TeacherAssignmentNew from './pages/teacher/AssignmentNew';
import TeacherAssignmentEdit from './pages/teacher/AssignmentEdit';
import TeacherAnalytics from './pages/teacher/Analytics';
import TeacherStudentView from './pages/teacher/StudentView';
import StudentDashboard from './pages/student/Dashboard';
import StudentAssignment from './pages/student/Assignment';
import StudentSummary from './pages/student/Summary';
import { getAuth, isAuthenticated } from './utils/auth';

function PrivateRoute({ children, requiredRole }: { children: JSX.Element; requiredRole?: 'teacher' | 'student' }) {
  const auth = getAuth();
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  
  if (requiredRole && auth.user?.role !== requiredRole) {
    return <Navigate to={auth.user?.role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard'} />;
  }
  
  return children;
}

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        <Route
          path="/teacher/dashboard"
          element={
            <PrivateRoute requiredRole="teacher">
              <TeacherDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/teacher/classrooms/:classroomId"
          element={
            <PrivateRoute requiredRole="teacher">
              <TeacherClassroom />
            </PrivateRoute>
          }
        />
        <Route
          path="/teacher/assignments/new"
          element={
            <PrivateRoute requiredRole="teacher">
              <TeacherAssignmentNew />
            </PrivateRoute>
          }
        />
        <Route
          path="/teacher/assignments/:assignmentId/edit"
          element={
            <PrivateRoute requiredRole="teacher">
              <TeacherAssignmentEdit />
            </PrivateRoute>
          }
        />
        <Route
          path="/teacher/analytics/:classroomId"
          element={
            <PrivateRoute requiredRole="teacher">
              <TeacherAnalytics />
            </PrivateRoute>
          }
        />
        <Route
          path="/teacher/classrooms/:classroomId/students/:studentId"
          element={
            <PrivateRoute requiredRole="teacher">
              <TeacherStudentView />
            </PrivateRoute>
          }
        />
        
        <Route
          path="/student/dashboard"
          element={
            <PrivateRoute requiredRole="student">
              <StudentDashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/student/assignments/:assignmentId"
          element={
            <PrivateRoute requiredRole="student">
              <StudentAssignment />
            </PrivateRoute>
          }
        />
        <Route
          path="/student/summary"
          element={
            <PrivateRoute requiredRole="student">
              <StudentSummary />
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

