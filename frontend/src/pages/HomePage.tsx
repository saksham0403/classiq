import { useNavigate } from 'react-router-dom';
import { getAuth, isAuthenticated } from '../utils/auth';

export default function HomePage() {
  const navigate = useNavigate();
  const auth = getAuth();
  const loggedIn = isAuthenticated();

  const getDashboardPath = () => {
    if (auth.user?.role === 'teacher') return '/teacher/dashboard';
    if (auth.user?.role === 'student') return '/student/dashboard';
    return '/login';
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation Bar */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-indigo-600">ClassIQ</h1>
            </div>
            <div className="flex items-center space-x-4">
              {loggedIn ? (
                <button
                  onClick={() => navigate(getDashboardPath())}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                  Go to Dashboard
                </button>
              ) : (
                <>
                  <button
                    onClick={() => navigate('/login')}
                    className="px-4 py-2 text-gray-700 hover:text-indigo-600 focus:outline-none transition-colors"
                  >
                    Sign in
                  </button>
                  <button
                    onClick={() => navigate('/signup')}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                  >
                    Get started
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl font-bold text-gray-900 leading-tight">
              ClassIQ – AI-powered classroom assistant for grading and insights
            </h1>
            <p className="mt-6 text-xl text-gray-600 leading-relaxed">
              Automate grading, uncover learning gaps, and give each student a clear path to improvement.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => navigate('/signup')}
                className="px-8 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 text-lg font-medium transition-colors"
              >
                Get started as a teacher
              </button>
              <button
                onClick={() => navigate('/login')}
                className="px-8 py-3 text-indigo-600 hover:text-indigo-700 focus:outline-none text-lg font-medium transition-colors"
              >
                Already have an account? Sign in
              </button>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-8 border border-indigo-100 shadow-lg">
              <div className="space-y-4">
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="h-4 bg-indigo-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="h-4 bg-green-200 rounded w-2/3 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="h-4 bg-indigo-200 rounded w-4/5 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/5"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Everything you need to manage your classroom
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Automated Grading</h3>
              <p className="text-gray-600">
                Grade numeric, algebra, and short answers in seconds.
              </p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Classroom Insights</h3>
              <p className="text-gray-600">
                See topic-level performance and the hardest questions.
              </p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Student Summaries</h3>
              <p className="text-gray-600">
                Show each student their strengths and weak topics.
              </p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="text-4xl mb-4">🔒</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Safe & Private</h3>
              <p className="text-gray-600">
                Built with privacy and education workflows in mind.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">1️⃣</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Create a class and assignment
              </h3>
              <p className="text-gray-600">
                Set up your classroom and add assignments with questions.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">2️⃣</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Students submit answers
              </h3>
              <p className="text-gray-600">
                Students complete assignments and submit their work.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">3️⃣</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                ClassIQ auto-grades and shows insights
              </h3>
              <p className="text-gray-600">
                Get instant grading results and detailed analytics.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Who It's For Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Who It's For
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg p-8 shadow-sm">
              <div className="text-4xl mb-4">👨‍🏫</div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Teachers</h3>
              <p className="text-gray-600 text-lg">
                Spend fewer hours grading, more time teaching. Get instant insights into student performance and identify areas that need attention.
              </p>
            </div>
            <div className="bg-white rounded-lg p-8 shadow-sm">
              <div className="text-4xl mb-4">👨‍🎓</div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Students</h3>
              <p className="text-gray-600 text-lg">
                Understand mistakes faster, know what to practice. Get personalized feedback and track your learning progress.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-600 mb-4 md:mb-0">
              © {new Date().getFullYear()} ClassIQ
            </div>
            <div className="flex space-x-6 text-gray-600">
              <a href="#" className="hover:text-indigo-600 transition-colors">About</a>
              <a href="#" className="hover:text-indigo-600 transition-colors">Contact</a>
              <a href="#" className="hover:text-indigo-600 transition-colors">Privacy</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

